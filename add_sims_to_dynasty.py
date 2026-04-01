# *Python Modules*
import traceback

# *Sims 4 Modules*
import services
import sims4.resources

from careers.career_enums import CareerCategory
from careers.career_tracker import CareerTracker

from dynasty.dynasty import Dynasty
from dynasty.dynasty_tunings import DynastyTunables

from interactions.utils.death import DeathTracker

from kingdom.kingdom_service import KingdomService
from kingdom.kingdom_tuning import KingdomTuning

from sims.genealogy_tracker import GenealogyTracker
from sims.sim_info import SimInfo
from sims.sim_info_types import Age

from relationships.relationship_tracker import RelationshipTracker

from zone import Zone

# *My Modules*
from . import constants

from .utils.injection import inject_to
from .utils.debug_logger import debug_log

# *Functions*

# Function Name: _get_sim_dynasty()
# Description: Takes a sim's SimInfo and checks if they're currently in a dynasty. The dynasty object is then returned if one is found, otherwise a None object is returned.
def _get_sim_dynasty(sim_info: SimInfo) -> Dynasty:
    try:
        sim_dynasty = services.dynasty_service().get_sim_dynasty(sim_info.id)
        return sim_dynasty
    except:
        debug_log("EXCEPTION when getting sim dynasty:\n" + traceback.format_exc())
        return None


# Function Name: _are_sims_related_or_married()
# Description: Checks if sim B is related (by 2 layers) to sim A or married.
def _are_sims_related_or_married(sim_info_a: SimInfo,sim_info_b: SimInfo) -> bool:
    return services.family_tree_service().are_sims_related(sim_info_a.id, sim_info_b.id, max_search_depth=2) or sim_info_a.spouse_sim_id == sim_info_b.id


# Function Name: _set_sim_as_noble_successor()
# Description: Sets a sim as another sim's noble successor if the latter is in the noble career.
def _set_sim_as_noble_successor(noble_sim_info: SimInfo,inheriting_sim_info: SimInfo) -> None:
    kingdom_service = services.kingdom_service()

    if kingdom_service.has_noble_career(noble_sim_info) and noble_sim_info != inheriting_sim_info:
        debug_log(f"Setting {inheriting_sim_info.first_name} {inheriting_sim_info.last_name} as {noble_sim_info.first_name} {noble_sim_info.last_name}'s noble successor.")
        kingdom_service.set_inheriting_sim(noble_sim_info,inheriting_sim_info)
                

# Function Name: _remove_fulltime_careers()
# Description: Removes all full time careers from a sim, which would conflict with the Noble career.
def _remove_fulltime_careers(sim_info: SimInfo) -> bool:
    career_tracker = services.sim_info_manager().get(sim_info.id).career_tracker

    if career_tracker == None:
        return False

    career_uids_to_remove = []

    for career_uid, career in career_tracker.careers.items():
        if career.career_category == CareerCategory.Work:
            career_uids_to_remove.append(career_uid)

    for career_uid in career_uids_to_remove:
        career_tracker.remove_career(career_uid, post_quit_msg=False, update_ui=True)

    return True


# Function Name: _add_noble_career()
# Description: Adds the noble career to a sim. For some reason, the in-built EA function does not work for this use-case.
def _add_noble_career(sim_info: SimInfo) -> bool:
    if not sim_info:
        return False
    
    kingdom_service = services.kingdom_service()

    if kingdom_service.has_noble_career(sim_info):
        return False
    
    career_tracker = services.sim_info_manager().get(sim_info.id).career_tracker
    new_career = KingdomTuning.NOBLE_CAREER(sim_info)
    career_tracker.add_career(new_career, show_confirmation_dialog=False)

    return True

# Function Name: _order_relative_list()
# Description: Takes a list of relative sim ids from the Genealogy Tracker and organises them from oldest to youngest for prioritising during assignment.
def _order_relative_list(relative_sim_ids) -> list:
        ordered_sim_infos = []
        for relative_sim_id in relative_sim_ids:
            relative_sim_info = services.sim_info_manager().get(relative_sim_id)
            if relative_sim_info is None:
                continue
            ordered_sim_infos.append(relative_sim_info)

        ordered_sim_infos.sort(
            key=lambda s: (s.age, s.age_progress),
            reverse=True
        )
        
        return ordered_sim_infos

def should_be_black_sheep(target_sim_info: SimInfo) -> bool:
    dynasty = _get_sim_dynasty(target_sim_info)

    if dynasty == None:
        return False

    head_sim_info = dynasty.get_head_sim_info()
    
    headmember_rel = head_sim_info.relationship_tracker.get_relationship_score(target_sim_info.id)

    if headmember_rel <= constants.MAXIMUM_REL_BLACKSHEEP_THRESHOLD:
        return True

    return False

# Function Name: _calculate_dynasty_heir()
# Description: Calculates the most suitable sim to become an unplayed dynasty's heir.

# PRIORITY LIST: Children (oldest-youngest), Spouses, Siblings (oldest-youngest), Parents (oldest-youngest)

# To qualify to be an heir, a sim must:
# - Have one of the above relations with the head.
# - Must have at least a +10% relationship with the head.
# - Must not be a dynasty outcast. (should not be possible if the above is true)
# - Must not be dead.
# - Must be an existing member of the dynasty.

# If there is an existing heir to the dynasty, they will only be replaced if they have less than a +10% relationship with the head. Otherwise, no new heir will be set.
# Should there be no sim that qualifies as heir, none will be set. Either the existing heir or the lowest ranking dynasty member will take over once the head steps down.
def _calculate_dynasty_heir(dynasty: Dynasty) -> None:
    kingdom_service = services.kingdom_service()
    
    head_sim_info = dynasty.get_head_sim_info()
    old_heir_sim_info = dynasty.get_heir_sim_info()

    if head_sim_info.household.is_player_household == True:
        return

    # Checking if old heir qualifies to be heir still.
    if old_heir_sim_info != None:
        headheir_rel = head_sim_info.relationship_tracker.get_relationship_score(old_heir_sim_info.id)
        
        if headheir_rel >= constants.MINIMUM_REL_HEIR_THRESHOLD: 
            return

    chosen_heir_sim_info = None

    # Checks if a sim qualifies to be heir by their SimInfo.
    def _can_be_heir(target_sim_info: SimInfo) -> bool:
        if target_sim_info == None:
            return False

        is_black_sheep = target_sim_info.has_trait(DynastyTunables.BLACK_SHEEP_TRAIT)
        
        if is_black_sheep and not should_be_black_sheep(target_sim_info):
            dynasty.set_black_sheep(target_sim_info,negate=True,update_client=True)
        
        headchild_rel = head_sim_info.relationship_tracker.get_relationship_score(target_sim_info.id)
        return not headchild_rel <= constants.MINIMUM_REL_HEIR_THRESHOLD and not target_sim_info.has_trait(DynastyTunables.BLACK_SHEEP_TRAIT) and not target_sim_info.is_dead and (target_sim_info.id in dynasty.get_members())

    head_children_sim_infos = _order_relative_list(list(head_sim_info.genealogy.get_children_sim_ids_gen()))

    # Checking children.
    for child_sim_info in head_children_sim_infos:
        if _can_be_heir(child_sim_info):
            chosen_heir_sim_info = child_sim_info

    # Checking spouse.
    if chosen_heir_sim_info == None:
        head_spouse_sim_id = head_sim_info.spouse_sim_id
        if head_spouse_sim_id != None:
            head_spouse_sim_info = services.sim_info_manager().get(head_spouse_sim_id)

            if _can_be_heir(head_spouse_sim_info):
                chosen_heir_sim_info = head_spouse_sim_info

    # Checking siblings.
    if chosen_heir_sim_info == None:
        head_siblings_sim_infos = _order_relative_list(list(head_sim_info.genealogy.get_siblings_sim_ids_gen()))

        for sibling_sim_info in head_siblings_sim_infos:
            if _can_be_heir(sibling_sim_info):
                chosen_heir_sim_info = sibling_sim_info

    # Checking parents.
    if chosen_heir_sim_info == None:
        head_parents_sim_infos = _order_relative_list(list(head_sim_info.genealogy.get_parent_sim_ids_gen()))

        for parent_sim_info in head_parents_sim_infos:
            if _can_be_heir(parent_sim_info):
                chosen_heir_sim_info = parent_sim_info

    # Setting as heir if a qualifying sim is found.
    if chosen_heir_sim_info != None:
        dynasty.set_heir(chosen_heir_sim_info.id,update_client=True)

# Function Name: _calculate_noble_successor()
# Description: Calculates the most suitable sim to become a noble sim's successor.

# PRIORITY LIST: Dynasty Heirs, Children (oldest-youngest), Spouses

# To qualify to be an heir, a sim:
# - Must be either the noble sim's spouse or child.
# - Must have at least a +0% relationship with the noble sim.
# - Must live in the same neighbourhood as the noble sim.
# - Must not be dead.
# - Must be at least a teenager.
# - Must not have a higher noble rank than the noble sim.

# If there are no qualifying successor sims found, the noble rank will be lost unless manually reclaimed by the player.
def _calculate_noble_successor(noble_sim_info: SimInfo) -> None:
    kingdom_service = services.kingdom_service()

    if noble_sim_info.household.is_player_household == True or not kingdom_service.has_noble_career(noble_sim_info) or not noble_sim_info:
        return

    noble_successor_sim_info = None
    
    # Checks if a sim qualifies to be successor by their SimInfo.
    def _can_be_successor(target_sim_info: SimInfo) -> bool:
        if target_sim_info == None:
            return False

        lower_noble_rank = True

        if kingdom_service.has_noble_career(target_sim_info):
            if kingdom_service.get_noble_career_level(target_sim_info.id) >= kingdom_service.get_noble_career_level(noble_sim_info.id):
                lower_noble_rank = False
        
        headchild_rel = noble_sim_info.relationship_tracker.get_relationship_score(target_sim_info.id)
        return not headchild_rel < constants.MINIMUM_REL_NOBLEINHERIT_THRESHOLD and not target_sim_info.is_dead and kingdom_service.get_sim_neighborhood_id(noble_sim_info) == kingdom_service.get_sim_neighborhood_id(target_sim_info) and target_sim_info.age >= Age.TEEN and lower_noble_rank
    
    noble_dynasty = _get_sim_dynasty(noble_sim_info)
    
    noble_children_sim_infos = _order_relative_list(list(noble_sim_info.genealogy.get_children_sim_ids_gen()))

    # Checking dynasty heirs.                                
    if noble_dynasty != None:
        if noble_dynasty.get_head_sim_info() == noble_sim_info:
            heir_sim_info = noble_dynasty.get_heir_sim_info()
            if heir_sim_info != None:
                if (heir_sim_info in noble_children_sim_infos or heir_sim_info.id == noble_sim_info.spouse_sim_id) and _can_be_successor(heir_sim_info):
                    noble_successor_sim_info = heir_sim_info

    # Checking children.
    if noble_successor_sim_info == None:                                  
        for child_sim_info in noble_children_sim_infos:
            if _can_be_successor(child_sim_info):
                noble_successor_sim_info = child_sim_info

    # Checking spouses.
    if noble_successor_sim_info == None:
        noble_spouse_sim_id = noble_sim_info.spouse_sim_id
        
        if noble_spouse_sim_id != None:
            noble_spouse_sim_info = services.sim_info_manager().get(noble_spouse_sim_id)

            if _can_be_successor(noble_spouse_sim_info):
                noble_successor_sim_info = noble_spouse_sim_info

    # Setting as successor if a qualifying sim is found.
    if noble_successor_sim_info != None:
        _set_sim_as_noble_successor(noble_sim_info,noble_successor_sim_info)

        
# Function Name: _calculate_dynasty_black_sheeps()
# Description: Calculates dynasty outcasts based on the relationship with the head.
# If a dynasty member has a -60% relationship or lower with the head sim, they will be outcasted in the dynasty.
# If an existing dynasty outcast has a +0% or more with the head sim, their outcast status will be revoked.
def _calculate_dynasty_black_sheeps(dynasty) -> None:
    head_sim_info = dynasty.get_head_sim_info()

    if head_sim_info == None:
        return

    if head_sim_info.household.is_player_household == True:
        return

    member_sim_ids = dynasty.get_members()

    for member_sim_id in member_sim_ids:
        member_sim_info = services.sim_info_manager().get(member_sim_id)
        if member_sim_info == None:
            continue
        
        if member_sim_id == dynasty.get_head_sim_id() or member_sim_id == dynasty.get_heir_sim_id():
            continue

        headmember_rel = head_sim_info.relationship_tracker.get_relationship_score(member_sim_id)

        is_black_sheep = member_sim_info.has_trait(DynastyTunables.BLACK_SHEEP_TRAIT)

        if is_black_sheep and headmember_rel > constants.MINIMUM_REL_REMOVEBLACKSHEEP_THRESHOLD:
            dynasty.set_black_sheep(member_sim_info,negate=True,update_client=True)
        elif not is_black_sheep and headmember_rel <= constants.MAXIMUM_REL_BLACKSHEEP_THRESHOLD:
            dynasty.set_black_sheep(member_sim_info,negate=False,update_client=True)


# Function Name: _check_child_for_dynasties()
# Description: Once a new child is born or adopted, this checks their parents for dynasties. If the parent is a head/heir of their dynasty, the child may be added.
# If both parents are in different dynasties which they are head/heirs of, the child will be added to whichever dynasty has the highest prestige.
def _check_child_for_dynasties(sim_info) -> None:
    if sim_info.household.is_player_household == True:
        return
    
    sim_is_in_dynasty = _get_sim_dynasty(sim_info) != None
    
    debug_log("**AUTODYNASTYMOD SIM CHECK**")
    debug_log(f"Sim Name: {sim_info.first_name} {sim_info.last_name}")
    debug_log(f"Sim Already In Dynasty: {sim_is_in_dynasty}")
    
    if sim_is_in_dynasty:
        return

    genealogy = sim_info.genealogy
    parent_sim_ids = genealogy.get_parent_sim_ids()

    parent_count = 0
    highest_dynasty = None

    debug_log(f"*SIM ({sim_info.first_name}'s) PARENTS*")

    for parent_sim_id in parent_sim_ids:
        parent_count += 1

        parent_sim_info = services.sim_info_manager().get(parent_sim_id)
        if parent_sim_info is None:
            continue

        debug_log(f"PARENT {parent_count}")
        debug_log(f"Parent Name: {parent_sim_info.first_name} {parent_sim_info.last_name}")

        parent_dynasty = _get_sim_dynasty(parent_sim_info)

        debug_log(f"Parent In Dynasty: {parent_dynasty != None}")
        
        if parent_dynasty == None:
            continue

        debug_log(f"Parent Dynasty Name: {parent_dynasty.name}")
        debug_log(f"Parent Dynasty Prestige: {parent_dynasty.get_prestige_value()}")
        
        if parent_sim_id != parent_dynasty.get_head_sim_id() and parent_sim_id != parent_dynasty.get_heir_sim_id():
            continue
        
        if highest_dynasty == None:
            highest_dynasty = parent_dynasty
        elif highest_dynasty != None and parent_dynasty != None:
            if parent_dynasty.get_prestige_value() > highest_dynasty.get_prestige_value():
                highest_dynasty = parent_dynasty

    if highest_dynasty != None:
        debug_log(f"Adding {sim_info.first_name} {sim_info.last_name} to {highest_dynasty.name} Dynasty.")
        highest_dynasty.add_member(sim_info,update_client=True)


# Function Name: _on_sim_marriage()
# Description: Once a marriage occurs, this function checks if either/both sims are in a dynasty and are the head/heir.
# If only one side is a head/heir of a dynasty, the other member will be added.
# If both are heads/heirs of a dynasty, the sim from the lower prestige dynasty will join the higher one.
def _on_sim_marriage(sim_info,spouse_sim_info):
    if sim_info.household.is_player_household == True or spouse_sim_info.household.is_player_household == True:
        return
    
    sim_dynasty = _get_sim_dynasty(sim_info)
    spouse_dynasty = _get_sim_dynasty(spouse_sim_info)

    sim_is_headheir = False
    spouse_is_headheir = False 

    debug_log("**AUTODYNASTYMOD SIM MARRIAGE CHECK**")
    debug_log(f"Sim Name: {sim_info.first_name} {sim_info.last_name}")
    debug_log(f"Spouse Name: {spouse_sim_info.first_name} {spouse_sim_info.last_name}")

    if sim_dynasty != None:
        sim_is_headheir = sim_info == sim_dynasty.get_head_sim_info() or sim_info == sim_dynasty.get_heir_sim_info()

    if spouse_dynasty != None:
        spouse_is_headheir = spouse_sim_info == spouse_dynasty.get_head_sim_info() or spouse_sim_info == spouse_dynasty.get_heir_sim_info()

    debug_log(f"Sim Is Dynasty Head/Heir: {sim_is_headheir}")
    debug_log(f"Spouse Is Dynasty Head/Heir: {spouse_is_headheir}")

    if sim_is_headheir == False and spouse_is_headheir == False:
        return
    elif sim_is_headheir == True and spouse_is_headheir == False:
        sim_dynasty.add_member(spouse_sim_info,update_client=True)
    elif sim_is_headheir == False and spouse_is_headheir == True:
        spouse_dynasty.add_member(sim_info,update_client=True)
    else:
        if sim_dynasty.get_prestige_value() > spouse_dynasty.get_prestige_value() and sim_is_headheir == True:
            debug_log(f"Adding {spouse_sim_info.first_name} {spouse_sim_info.last_name} to {sim_dynasty.name} Dynasty.")
            sim_dynasty.add_member(spouse_sim_info,update_client=True)
        else:
            debug_log(f"Adding {sim_info.first_name} {sim_info.last_name} to {spouse_dynasty.name} Dynasty.")
            spouse_dynasty.add_member(sim_info,update_client=True)


# Function Name: _calculate_dynasty_relations()
# Description: Calculates the relations between different dynasties based on relations to the head or dynasty to a whole.
# To create a new alliance, a head sim must either be friends with the dynasty head or have a positive average relationship with the members. (the alliance must also be within the set level gap)
# To create a new rivalry, a head sim must have a poor relationship with another head sim or average across all members.
# To remove an existing alliance, a head sim must not have a positive relationship with another and must have a small or negative average relationship with all members.
# To remove an existing rivalry, a head sim must have a positive relationship with the other head sim.
def _calculate_dynasty_relations(main_dynasty: Dynasty) -> None:
    if not constants.AUTO_RELATIONS_ENABLED == True:
        return

    dynasty_service = services.dynasty_service()
    sim_info_manager = services.sim_info_manager()

    main_head_sim_info = main_dynasty.get_head_sim_info()
    
    if main_head_sim_info == None or dynasty_service == None or sim_info_manager == None:
        return

    if main_head_sim_info.household.is_player_household == True:
        return

    def _calculate_average_dynasty_rel(target_dynasty: Dynasty):
        rel_total = 0
        target_member_sim_ids = target_dynasty.get_members()

        for member_sim_id in target_member_sim_ids:
            if member_sim_id == None:
                continue
            rel_total += main_head_sim_info.relationship_tracker.get_relationship_score(member_sim_id)

        return rel_total / len(target_member_sim_ids)

    main_dynasty_prestige_level = main_dynasty.get_total_prestige_stat().rank_level

    debug_log(f"*DYNASTY RELATIONS CHECK*")
    debug_log(f"Dynasty name: {main_dynasty.name}")
    debug_log(f"Dynasty Prestige Level: {main_dynasty_prestige_level}")

    dynasty_allies = list(main_dynasty._alliances)

    for ally_dynasty_id in dynasty_allies:
        ally_dynasty = dynasty_service.get_dynasty(ally_dynasty_id)

        if ally_dynasty == None or ally_dynasty == main_dynasty:
            continue

        ally_head_sim_info = ally_dynasty.get_head_sim_info()

        if ally_head_sim_info == None:
            continue
        elif ally_head_sim_info.household.is_player_household == True:
            continue

        if main_dynasty.is_rival(ally_dynasty):
            dynasty_service.end_rivalry(main_dynasty,ally_dynasty)

        ally_head_rel = main_head_sim_info.relationship_tracker.get_relationship_score(ally_head_sim_info.id)
        ally_average_rel = _calculate_average_dynasty_rel(ally_dynasty)

        debug_log(f"Ally Dynasty name: {ally_dynasty.name}")
        debug_log(f"Ally Head Relationship: {ally_head_rel}")
        debug_log(f"Ally Average Relationship: {ally_average_rel}")

        if (ally_head_rel <= constants.MAXIMUM_HEAD_REL_REMOVE_ALLY and ally_average_rel <= constants.MAXIMUM_AVERAGE_REL_REMOVE_ALLY):
            debug_log(f"Removing {ally_dynasty.name} as {main_dynasty.name} ally.")
            dynasty_service.end_alliance(main_dynasty,ally_dynasty)

    dynasty_rivals = list(main_dynasty._rivalries)

    for rival_dynasty_id in dynasty_rivals:
        rival_dynasty = dynasty_service.get_dynasty(rival_dynasty_id)

        if rival_dynasty == None or rival_dynasty == main_dynasty:
            continue

        rival_head_sim_info = rival_dynasty.get_head_sim_info()

        if rival_head_sim_info == None:
            continue
        elif rival_head_sim_info.household.is_player_household == True:
            continue
        
        rival_head_rel = main_head_sim_info.relationship_tracker.get_relationship_score(rival_head_sim_info.id)

        debug_log(f"Rival Dynasty name: {rival_dynasty.name}")
        debug_log(f"Rival Head Relationship: {rival_head_rel}")
        
        if rival_head_rel >= constants.MINIMUM_HEAD_REL_REMOVE_RIVAL:
            debug_log(f"Removing {rival_dynasty.name} as {main_dynasty.name} rival.")
            dynasty_service.end_rivalry(main_dynasty,rival_dynasty)

    all_dynasties = dynasty_service.get_all_dynasties()

    for target_dynasty in all_dynasties.values():
        if target_dynasty == None:
            continue
        elif target_dynasty == main_dynasty or main_dynasty.is_ally(target_dynasty) or main_dynasty.is_rival(target_dynasty):
            continue

        target_head_sim_info = target_dynasty.get_head_sim_info()

        if target_head_sim_info == None:
            continue
        elif target_head_sim_info.household.is_player_household == True:
            continue

        target_head_rel = main_head_sim_info.relationship_tracker.get_relationship_score(target_head_sim_info.id)
        target_average_rel = _calculate_average_dynasty_rel(target_dynasty)

        target_dynasty_prestige_level = main_dynasty.get_total_prestige_stat().rank_level

        debug_log(f"Target Dynasty name: {target_dynasty.name}")
        debug_log(f"Target Head Relationship: {target_head_rel}")
        debug_log(f"Target Average Relationship: {target_average_rel}")
        debug_log(f"Target Prestige Level: {target_dynasty_prestige_level}")

        if (target_head_rel >= constants.MINIMUM_HEAD_REL_NEW_ALLY or target_average_rel >= constants.MINIMUM_AVERAGE_REL_NEW_ALLY) and target_dynasty_prestige_level in range(main_dynasty_prestige_level - constants.MAXIMUM_LOWER_LEVEL_GAP_ALLY, main_dynasty_prestige_level + constants.MAXIMUM_LOWER_LEVEL_GAP_ALLY):
            debug_log(f"Adding {target_dynasty.name} as {main_dynasty.name} ally.")
            dynasty_service.add_alliance(main_dynasty,target_dynasty)
        elif (target_head_rel <= constants.MAXIMUM_HEAD_REL_NEW_RIVAL or target_average_rel <= constants.MAXIMUM_AVERAGE_REL_NEW_RIVAL):
            debug_log(f"Adding {target_dynasty.name} as {main_dynasty.name} rival.")
            dynasty_service.add_rivalry(main_dynasty,target_dynasty)


# *Hooks*

# Runs when the parent relationship is set for a sim. Presumably when a child is born or adopted.
# The child is checked for any valid dynasties.
@inject_to(GenealogyTracker, "set_parent_relation")
def _hook_genealogy_tracker_set_parent_relation(original, self, *args, **kwargs):
    debug_log("HOOK: GenealogyTracker.set_parent_relation fired")
    result = original(self,*args,**kwargs)
    try:
        child_sim_id = self._owner_id
        child_sim_info = services.sim_info_manager().get(child_sim_id)
        
        _check_child_for_dynasties(child_sim_info)
    except:
        debug_log("EXCEPTION in GenealogyTracker.set_parent_relation hook:\n" + traceback.format_exc())
    return result


# Runs when a new relationship bit is added between two sims.
# This is used to detect when a marriage happens or when two sims of the same dynasty have a relationship change.
# This allows for dynasty hierarchies to change with NPC dynasty member relationship changes. (such as heirs changing or members being outcasted)
# This too, also allows for noble successors to be changed.
@inject_to(RelationshipTracker, "add_relationship_bit")
def _hook_relationship_tracker_add_relationship_bit(original, self, target_sim_id, bit, *args, **kwargs):
    debug_log("HOOK: RelationshipTracker.add_relationship_bit fired")
    result = original(self, target_sim_id, bit, *args, **kwargs)
    try:
        kingdom_service = services.kingdom_service()
        
        sim_info = self._sim_info
        target_sim_info = services.sim_info_manager().get(target_sim_id)
        
        if sim_info != None and target_sim_info != None:
            if "romantic-married" in str(bit).lower():
                _on_sim_marriage(sim_info,target_sim_info)

            sim_a_dynasty = _get_sim_dynasty(sim_info)
            sim_b_dynasty = _get_sim_dynasty(target_sim_info)

            if (sim_a_dynasty == sim_b_dynasty) and sim_a_dynasty != None:
                _calculate_dynasty_heir(sim_a_dynasty)
                _calculate_dynasty_black_sheeps(sim_a_dynasty)
            elif (sim_a_dynasty != None and sim_b_dynasty != None and sim_a_dynasty != sim_b_dynasty):
                _calculate_dynasty_relations(sim_a_dynasty)
                _calculate_dynasty_relations(sim_b_dynasty)

            sim_a_is_noble = kingdom_service.has_noble_career(sim_info)
            sim_b_is_noble = kingdom_service.has_noble_career(target_sim_info)
            
            if _are_sims_related_or_married(sim_info,target_sim_info) and (sim_a_is_noble or sim_b_is_noble):
                if sim_a_is_noble:
                    _calculate_noble_successor(sim_info)
                if sim_b_is_noble:
                    _calculate_noble_successor(target_sim_info)
    except:
        debug_log("EXCEPTION in RelationshipTracker.add_relationship_bit hook:\n" + traceback.format_exc())
    return result


# Runs when a new sim is added into a dynasty.
# This allows for dynasty hierarchies to change when new members are introduced through birth, adoption or marriages. (such as heirs changing or members being outcasted)
@inject_to(Dynasty, "add_member")
def _hook_dynasty_add_member(original, self, *args, **kwargs):
    debug_log("HOOK: Dynasty.add_member fired")
    result = original(self, *args, **kwargs)
    try:
        _calculate_dynasty_heir(self)
        _calculate_dynasty_black_sheeps(self)
    except:
        debug_log("EXCEPTION in Dynasty.add_member hook:\n" + traceback.format_exc())
    return result


# Runs when a dynasty member is removed from the dynasty.
# This allows for dynasty hierarchies to change when new members are removed through birth, adoption or marriages. (such as heirs changing or members being outcasted)
@inject_to(Dynasty, "remove_member")
def _hook_dynasty_remove_member(original, self, target_sim_id, *args, **kwargs):
    debug_log("HOOK: Dynasty.remove_member fired")
    
    result = original(self, target_sim_id, *args, **kwargs)
    
    try:
        _calculate_dynasty_heir(self)
        _calculate_dynasty_black_sheeps(self)
    except:
        debug_log("EXCEPTION in Dynasty.remove_member hook:\n" + traceback.format_exc())
    return result


# Runs when a zone finishes loading all sims.
# Probably redundant, but allows for existing dynasties to be updated after each zone load.
@inject_to(Zone, "on_all_sims_spawned")
def _hook_zone_on_all_sims_spawned(original, self, *args, **kwargs):
    debug_log("HOOK: Zone.on_all_sims_spawned fired")
    result = original(self, *args, **kwargs)
    try:
        all_dynasties = services.dynasty_service().get_all_dynasties()

        for dynasty in all_dynasties.values():
            _calculate_dynasty_heir(dynasty)
            _calculate_dynasty_black_sheeps(dynasty)
            _calculate_dynasty_relations(dynasty)
    except:
        debug_log("EXCEPTION in Zone.on_all_sims_spawned hook:\n" + traceback.format_exc())
    return result


# Runs after a noble sim with an inheriting sim dies.
# Sets up the sim to become a valid target for inheritance.
# Removes the sim's existing career and gives them the noble career if they live in the same neighbourhood, aren't dead and are at least a teenager.
# This should fulfil the requirements needed for EA to process the inheriting sim after this hook so that they inherit the noble rank.
@inject_to(KingdomService, "process_inheriting_sim")
def _hook_kingdomservice_process_inhertiing_sim(original, self, neighborhood_id, noble_sim_info, inheriting_sim_id, *args, **kwargs):
    debug_log("HOOK: KingdomService.process_inheriting_sim fired")
    try:
        debug_log("**NOBLE DEATH**")
        debug_log(f"Noble Sim Name: {noble_sim_info.first_name} {noble_sim_info.last_name}")
        
        inheriting_sim_info = services.sim_info_manager().get(inheriting_sim_id)

        if inheriting_sim_info != None:
            debug_log(f"Inheriting Sim Name: {inheriting_sim_info.first_name} {inheriting_sim_info.last_name}")
            
            if noble_sim_info.household.is_player_household != True and inheriting_sim_info.household.is_player_household != True:
                debug_log(f"Inheriting Sim Lives in Kingdom: {self.get_sim_neighborhood_id(inheriting_sim_info) == neighborhood_id}")
                
                if self.get_sim_neighborhood_id(inheriting_sim_info) == neighborhood_id and not inheriting_sim_info.is_dead and inheriting_sim_info.age >= Age.TEEN:
                    if self.has_noble_career(inheriting_sim_info) == False:
                        debug_log(f"Remove {inheriting_sim_info.first_name}'s Adult Careers")

                        if _remove_fulltime_careers(inheriting_sim_info):
                            debug_log(f"Giving {inheriting_sim_info.first_name} Noble Career")
                            _add_noble_career(inheriting_sim_info)
    except:
        debug_log("EXCEPTION in KingdomService.process_inheriting_sim hook:\n" + traceback.format_exc())
        
    result = original(self, neighborhood_id, noble_sim_info, inheriting_sim_id, *args, **kwargs)
    return result


# Runs before a sim's death type is set. (Usually before the sim dies)
# Used to calculate the noble successor just before the noble sim dies, in case the current inheriting sim no longer qualifies.
# This is done to lower the risk of the noble rank being lost, and carried out over generations.
@inject_to(DeathTracker, "set_death_type")
def _hook_deathtracker_set_death_type(original, self, *args, **kwargs):
    debug_log("HOOK: DeathTracker.set_death_type fired")
    try:
        kingdom_service = services.kingdom_service()
        
        dying_sim_info = self._sim_info
        if dying_sim_info != None:
            debug_log("**SIM ABOUT TO DIE**")
            debug_log(f"Dying Sim Name: {dying_sim_info.first_name} {dying_sim_info.last_name}")

            is_noble = kingdom_service.has_noble_career(dying_sim_info)

            debug_log(f"Is Noble: {is_noble}")
            
            if dying_sim_info.household.is_player_household != True and is_noble == True:
                _calculate_noble_successor(dying_sim_info)
    except:
        debug_log("EXCEPTION in DeathTracker.set_death_type hook:\n" + traceback.format_exc())
        
    result = original(self, *args, **kwargs)
    return result


# Runs when a new career is added.
# Checks if the sim with the new career has the noble career (probably a better way to do this, but it works)
# If they do, their noble successor is calculated.
@inject_to(CareerTracker, "add_career")
def _hook_careertracker_add_career(original, self, *args, **kwargs):
    debug_log("HOOK: CareerTracker.add_career fired")
    result = original(self, *args, **kwargs)
    try:
        kingdom_service = services.kingdom_service()

        sim_info = self._sim_info

        if sim_info != None:
            is_noble = kingdom_service.has_noble_career(sim_info)

            if sim_info.household.is_player_household != True and is_noble == True:
                debug_log("**NOBLE SIM JOINED CAREER**")
                debug_log(f"Sim Name: {sim_info.first_name} {sim_info.last_name}")
                _calculate_noble_successor(sim_info)
    except:
        debug_log("EXCEPTION in CareerTracker.add_career hook:\n" + traceback.format_exc())
        
    return result
