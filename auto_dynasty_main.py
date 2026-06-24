# *Python Modules*
import traceback

# *Sims 4 Modules*
import services
import sims4.resources

import alarms

import date_and_time

from careers.career_enums import CareerCategory
from careers.career_tracker import CareerTracker

from protocolbuffers import GameplaySaveData_pb2, DistributorOps_pb2
from distributor.rollback import ProtocolBufferRollback

from dynasty.dynasty import Dynasty, DynastyMessageType
from dynasty.dynasty_service import DynastyService
from dynasty.dynasty_tunings import DynastyTunables

from event_testing.test_events import TestEvent

from relationships.global_relationship_tuning import RelationshipGlobalTuning
from relationships.relationship_enums import RelationshipType

from interactions.utils.death import DeathTracker

from kingdom.kingdom_service import KingdomService
from kingdom.kingdom_tuning import KingdomTuning

from sims.genealogy_tracker import GenealogyTracker
from sims.outfits.outfit_enums import BodyType, OutfitCategory
from sims.sim_info import SimInfo
from sims.sim_info_types import Age, Gender

from relationships.relationship_tracker import RelationshipTracker

# *My Modules*
from .auto_dynasty_settings import SETTINGS
from . import constants

from .utils.injection import inject_to
from .utils.debug_logger import debug_log

import sims4
logger = sims4.log.Logger('Dynasty')

# *Global Variables*

daily_check_alarm_handle = None

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
    if sim_info_a is None or sim_info_b is None:
        return False
    return services.family_tree_service().are_sims_related(sim_info_a.id, sim_info_b.id, max_search_depth=2) or sim_info_a.spouse_sim_id == sim_info_b.id
    

# Function Name: _is_dynasty_played()
# Description: Checks if a dynasty has any played sim members.
def _is_dynasty_played(dynasty: Dynasty) -> bool:
    if not dynasty:
        return None
    try:
        sim_info_manager = services.sim_info_manager()

        member_sim_ids = list(dynasty.get_members())

        for member_sim_id in member_sim_ids:
            member_sim_info = sim_info_manager.get(member_sim_id)

            if member_sim_info is None:
                continue

            if member_sim_info.household.is_player_household == True:
                return True
        
        return False
    except:
        debug_log("EXCEPTION when checking if dynasty played:\n" + traceback.format_exc())
        return None

def _calculate_sim_for_dynasty(target_sim_info) -> Dynasty:
    family_tree_service = services.family_tree_service()

    if target_sim_info is None:
        return
    
    viable_dynasties = []

    for dynasty in list(services.dynasty_service()._dynasties.values()):
        if dynasty is None:
            continue

        is_played = _is_dynasty_played(dynasty)

        head_sim_info = dynasty.get_head_sim_info()

        if head_sim_info is None or (not SETTINGS.enable_repair_for_played and is_played) or (not SETTINGS.enable_repair_for_unplayed and not is_played):
            continue
        
        children = family_tree_service.get_family_relation_sim_ids(target_sim_info.id,RelationshipType.DESCENDANT)
        spouses = family_tree_service.get_family_relation_sim_ids(target_sim_info.id,RelationshipType.SPOUSE)
        siblings = family_tree_service.get_family_relation_sim_ids(target_sim_info.id,RelationshipType.SIBLING)
        halfsiblings = family_tree_service.get_family_relation_sim_ids(target_sim_info.id,RelationshipType.HALF_SIBLING)
        parents = family_tree_service.get_family_relation_sim_ids(target_sim_info.id,RelationshipType.PARENT)
        grandchildren = family_tree_service.get_family_relation_sim_ids(target_sim_info.id,RelationshipType.GRANDCHILD)
        grandparents = family_tree_service.get_family_relation_sim_ids(target_sim_info.id,RelationshipType.GRANDPARENT)
        piblings = family_tree_service.get_family_relation_sim_ids(target_sim_info.id,RelationshipType.PARENTS_SIBLING)
        niblings = family_tree_service.get_family_relation_sim_ids(target_sim_info.id,RelationshipType.SIBLINGS_CHILD)
        
        dynasty_viable = False

        heir_sim_info = dynasty.get_heir_sim_info()
        
        if _are_sims_related_or_married(head_sim_info,target_sim_info) and "head" in SETTINGS.add_which_roles:
            if head_sim_info.id in children:
                # sim is head's parent
                if int(RelationshipType.PARENT) in SETTINGS.whitelist_head_relatives:
                    dynasty_viable = True
            elif head_sim_info.id in spouses:
                # sim is head's spouse
                if int(RelationshipType.SPOUSE) in SETTINGS.whitelist_head_relatives:
                    dynasty_viable = True
            elif head_sim_info.id in siblings:
                # sim is head's sibling
                if int(RelationshipType.SIBLING) in SETTINGS.whitelist_head_relatives:
                    dynasty_viable = True
            elif head_sim_info.id in halfsiblings:
                # sim is head's half-sibling
                if int(RelationshipType.HALF_SIBLING) in SETTINGS.whitelist_head_relatives:
                    dynasty_viable = True       
            elif head_sim_info.id in parents:
                # sim is head's child
                if int(RelationshipType.DESCENDANT) in SETTINGS.whitelist_head_relatives:
                    dynasty_viable = True
            elif head_sim_info.id in grandchildren:
                # sim is head's grandparent
                if int(RelationshipType.GRANDPARENT) in SETTINGS.whitelist_head_relatives:
                    dynasty_viable = True
            elif head_sim_info.id in grandparents:
                # sim is head's grandchild
                if int(RelationshipType.GRANDCHILD) in SETTINGS.whitelist_head_relatives:
                    dynasty_viable = True
            elif head_sim_info.id in piblings:
                # sim is head's niece/nephew
                if int(RelationshipType.SIBLINGS_CHILD) in SETTINGS.whitelist_head_relatives:
                    dynasty_viable = True
            elif head_sim_info.id in niblings:
                # sim is head's aunt/uncle.
                if int(RelationshipType.PARENTS_SIBLING) in SETTINGS.whitelist_head_relatives:
                    dynasty_viable = True
        
        if heir_sim_info is not None:
            if _are_sims_related_or_married(heir_sim_info,target_sim_info) and "heir" in SETTINGS.add_which_roles and not dynasty_viable:
                if heir_sim_info.id in children:
                    if int(RelationshipType.PARENT) in SETTINGS.whitelist_heir_relatives:
                        dynasty_viable = True
                elif heir_sim_info.id in spouses:
                    if int(RelationshipType.SPOUSE) in SETTINGS.whitelist_heir_relatives:
                        dynasty_viable = True
                elif heir_sim_info.id in siblings:
                    if int(RelationshipType.SIBLING) in SETTINGS.whitelist_heir_relatives:
                        dynasty_viable = True
                elif heir_sim_info.id in halfsiblings:
                    if int(RelationshipType.HALF_SIBLING) in SETTINGS.whitelist_heir_relatives:
                        dynasty_viable = True       
                elif heir_sim_info.id in parents:
                    if int(RelationshipType.DESCENDANT) in SETTINGS.whitelist_heir_relatives:
                        dynasty_viable = True
                elif heir_sim_info.id in grandchildren:
                    if int(RelationshipType.GRANDPARENT) in SETTINGS.whitelist_heir_relatives:
                        dynasty_viable = True
                elif heir_sim_info.id in grandparents:
                    if int(RelationshipType.GRANDCHILD) in SETTINGS.whitelist_heir_relatives:
                        dynasty_viable = True
                elif heir_sim_info.id in piblings:
                    if int(RelationshipType.SIBLINGS_CHILD) in SETTINGS.whitelist_heir_relatives:
                        dynasty_viable = True
                elif heir_sim_info.id in niblings:
                    if int(RelationshipType.PARENTS_SIBLING) in SETTINGS.whitelist_heir_relatives:
                        dynasty_viable = True
        
        if "member" in SETTINGS.add_which_roles and not dynasty_viable:
            member_sim_ids = list(dynasty.get_members())
            for member_sim_id in member_sim_ids:
                member_sim_info = services.sim_info_manager().get(member_sim_id)
                if member_sim_info is None or member_sim_info is head_sim_info or member_sim_info is heir_sim_info:
                    continue
                if _are_sims_related_or_married(member_sim_info,target_sim_info):
                    if member_sim_info.id in children:
                        if int(RelationshipType.PARENT) in SETTINGS.whitelist_member_relatives:
                            dynasty_viable = True
                    elif member_sim_info.id in spouses:
                        if int(RelationshipType.SPOUSE) in SETTINGS.whitelist_member_relatives:
                            dynasty_viable = True
                    elif member_sim_info.id in siblings:
                        if int(RelationshipType.SIBLING) in SETTINGS.whitelist_member_relatives:
                            dynasty_viable = True
                    elif member_sim_info.id in halfsiblings:
                        if int(RelationshipType.HALF_SIBLING) in SETTINGS.whitelist_member_relatives:
                            dynasty_viable = True       
                    elif member_sim_info.id in parents:
                        debug_log(SETTINGS.whitelist_member_relatives)
                        if int(RelationshipType.DESCENDANT) in SETTINGS.whitelist_member_relatives:
                            dynasty_viable = True
                    elif member_sim_info.id in grandchildren:
                        if int(RelationshipType.GRANDPARENT) in SETTINGS.whitelist_member_relatives:
                            dynasty_viable = True
                    elif member_sim_info.id in grandparents:
                        if int(RelationshipType.GRANDCHILD) in SETTINGS.whitelist_member_relatives:
                            dynasty_viable = True
                    elif member_sim_info.id in piblings:
                        if int(RelationshipType.SIBLINGS_CHILD) in SETTINGS.whitelist_member_relatives:
                            dynasty_viable = True
                    elif member_sim_info.id in niblings:
                        if int(RelationshipType.PARENTS_SIBLING) in SETTINGS.whitelist_member_relatives:
                            dynasty_viable = True

        if dynasty_viable == True:
            viable_dynasties.append(dynasty)

    if len(viable_dynasties) == 0:
        return
    
    highest_prior_dynasty = viable_dynasties[0]

    for dynasty in viable_dynasties:
        if _is_dynasty_played(dynasty):
            highest_prior_dynasty = dynasty
            break
        elif _get_highest_prestige_dynasty(dynasty,highest_prior_dynasty) is dynasty:
            highest_prior_dynasty = dynasty

    return highest_prior_dynasty

# Function Name: _set_sim_as_noble_successor()
# Description: Sets a sim as another sim's noble successor if the latter is in the noble career.
def _set_sim_as_noble_successor(noble_sim_info: SimInfo,inheriting_sim_info: SimInfo) -> None:
    kingdom_service = services.kingdom_service()

    if noble_sim_info is None or inheriting_sim_info is None:
        return

    noble_neighborhood_id = kingdom_service.get_sim_neighborhood_id(noble_sim_info)
    inherit_neighborhood_id = kingdom_service.get_sim_neighborhood_id(inheriting_sim_info)

    if noble_neighborhood_id is None or noble_neighborhood_id != inherit_neighborhood_id:
        return

    kingdom_data = kingdom_service.get_or_create_neighborhood_data(noble_neighborhood_id)
    if kingdom_data is not None:
        inherirting_sim_data = kingdom_service.get_sim_data(kingdom_data, inheriting_sim_info.id)
        if kingdom_service.has_noble_career(noble_sim_info) and noble_sim_info != inheriting_sim_info and inherirting_sim_data is not None:
            debug_log(f"Setting {inheriting_sim_info.first_name} {inheriting_sim_info.last_name} as {noble_sim_info.first_name} {noble_sim_info.last_name}'s noble successor.")
            kingdom_service.set_inheriting_sim(noble_sim_info,inheriting_sim_info)
                

# Function Name: _remove_fulltime_careers()
# Description: Removes all full time careers from a sim, which would conflict with the Noble career.
def _remove_fulltime_careers(sim_info: SimInfo) -> bool:
    career_tracker = sim_info.career_tracker

    if career_tracker is None:
        return False

    career_uids_to_remove = []

    for career_uid, career in career_tracker.careers.items():
        if career.career_category == CareerCategory.Work and not career_uid == KingdomTuning.NOBLE_CAREER.guid64:
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
    career_tracker.add_career(new_career, show_confirmation_dialog=False, show_join_msg=False)

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

    if dynasty is None:
        return False

    head_sim_info = dynasty.get_head_sim_info()
    
    if head_sim_info is None:
        return False

    headmember_rel = head_sim_info.relationship_tracker.get_relationship_score(target_sim_info.id)

    if headmember_rel <= SETTINGS.maximum_rel_blacksheep_threshold:
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
    if (SETTINGS.automatic_heir_selection and SETTINGS.global_dynasty_mod_enabler) is not True:
        return

    kingdom_service = services.kingdom_service()
    
    head_sim_info = dynasty.get_head_sim_info()
    old_heir_sim_info = dynasty.get_heir_sim_info()

    if head_sim_info is None:
        return

    if _is_dynasty_played(dynasty)  == True:
        return

    chosen_heir_sim_info = None

    # Checks if a sim qualifies to be heir by their SimInfo.
    def _can_be_heir(target_sim_info: SimInfo) -> bool:
        if target_sim_info is None:
            return False

        is_black_sheep = target_sim_info.has_trait(DynastyTunables.BLACK_SHEEP_TRAIT)
        
        if is_black_sheep and not should_be_black_sheep(target_sim_info):
            dynasty.set_black_sheep(target_sim_info,negate=True,update_client=True)

        minimum_age = Age(SETTINGS.heir_minimum_age)
        
        headchild_rel = head_sim_info.relationship_tracker.get_relationship_score(target_sim_info.id)
        return not headchild_rel <= SETTINGS.minimum_rel_heir_threshold and not target_sim_info.has_trait(DynastyTunables.BLACK_SHEEP_TRAIT) and not target_sim_info.is_dead and (target_sim_info.id in dynasty.get_members()) and minimum_age.sequential_value <= target_sim_info.age.sequential_value

    head_children_sim_infos = _order_relative_list(list(head_sim_info.genealogy.get_children_sim_ids_gen()))

    # Checking if old heir qualifies to be heir still.
    if old_heir_sim_info is not None and SETTINGS.keep_existing_heir:
        if _can_be_heir(old_heir_sim_info):
            return

    # Checking children.
    if "children" in SETTINGS.familial_connections_become_heir:
        for child_sim_info in head_children_sim_infos:
            if _can_be_heir(child_sim_info):
                priority_gender = getattr(Gender,SETTINGS.heir_gender_priority,child_sim_info.gender)

                if child_sim_info.gender == priority_gender:
                    if chosen_heir_sim_info is not None:
                        if chosen_heir_sim_info.gender != priority_gender:
                            chosen_heir_sim_info = child_sim_info
                
                if chosen_heir_sim_info is None:
                    chosen_heir_sim_info = child_sim_info


    # Checking spouse.
    if chosen_heir_sim_info is None and "spouse" in SETTINGS.familial_connections_become_heir:
        head_spouse_sim_id = head_sim_info.spouse_sim_id
        if head_spouse_sim_id is not None:
            head_spouse_sim_info = services.sim_info_manager().get(head_spouse_sim_id)

            if _can_be_heir(head_spouse_sim_info):
                chosen_heir_sim_info = head_spouse_sim_info

    # Checking siblings.
    if chosen_heir_sim_info is None and "siblings" in SETTINGS.familial_connections_become_heir:
        head_siblings_sim_infos = _order_relative_list(list(head_sim_info.genealogy.get_siblings_sim_ids_gen()))

        for sibling_sim_info in head_siblings_sim_infos:
            if _can_be_heir(sibling_sim_info):
                priority_gender = getattr(Gender,SETTINGS.heir_gender_priority,sibling_sim_info.gender)

                if sibling_sim_info.gender == priority_gender:
                    if chosen_heir_sim_info is not None:
                        if chosen_heir_sim_info.gender != priority_gender:
                            chosen_heir_sim_info = sibling_sim_info

                if chosen_heir_sim_info is None:
                    chosen_heir_sim_info = sibling_sim_info

    # Checking parents.
    if chosen_heir_sim_info is None and "parents" in SETTINGS.familial_connections_become_heir:
        head_parents_sim_infos = _order_relative_list(list(head_sim_info.genealogy.get_parent_sim_ids_gen()))

        for parent_sim_info in head_parents_sim_infos:
            if _can_be_heir(parent_sim_info):
                priority_gender = getattr(Gender,SETTINGS.heir_gender_priority,parent_sim_info.gender)

                if parent_sim_info.gender == priority_gender:
                    if chosen_heir_sim_info is not None:
                        if chosen_heir_sim_info.gender != priority_gender:
                            chosen_heir_sim_info = parent_sim_info

                if chosen_heir_sim_info is None:
                    chosen_heir_sim_info = parent_sim_info

    old_heir_sim_info = dynasty.get_heir_sim_info()

    # Setting as heir if a qualifying sim is found.
    if chosen_heir_sim_info is not None and old_heir_sim_info is not chosen_heir_sim_info:
        if old_heir_sim_info is not None:
            old_heir_sim_info.remove_trait(DynastyTunables.HEIR_TRAIT)
        dynasty._heir_sim_id = chosen_heir_sim_info.id
        dynasty.distribute_dynasty_msg(DynastyMessageType.UPDATE)
        chosen_heir_sim_info.add_trait(DynastyTunables.HEIR_TRAIT)
        

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
    if SETTINGS.global_noble_mod_enabler is not True:
        return

    kingdom_service = services.kingdom_service()

    if noble_sim_info is None:
        return

    if noble_sim_info.household.is_player_household == True or not kingdom_service.has_noble_career(noble_sim_info) or kingdom_service.get_sim_neighborhood_id(noble_sim_info) is None:
        return

    noble_successor_sim_info = None
    
    # Checks if a sim qualifies to be successor by their SimInfo.
    def _can_be_successor(target_sim_info: SimInfo) -> bool:
        if target_sim_info is None:
            return False

        lower_noble_rank = True

        if kingdom_service.has_noble_career(target_sim_info):
            if kingdom_service.get_noble_career_level(target_sim_info.id) >= kingdom_service.get_noble_career_level(noble_sim_info.id):
                lower_noble_rank = False

        minimum_age = Age(SETTINGS.nobleinherit_minimum_age)
        
        headchild_rel = noble_sim_info.relationship_tracker.get_relationship_score(target_sim_info.id)

        debug_log("SIM CHECK FOR INHERITANCE")
        debug_log(f"Sim Name: {target_sim_info.first_name} {target_sim_info.last_name}")
        debug_log(f"Meets Rel Needs: {not headchild_rel < SETTINGS.minimum_rel_nobleinherit_threshold}")
        debug_log(f"Is Dead: {target_sim_info.is_dead}")
        debug_log(f"Lives in same neighbourhood: {kingdom_service.get_sim_neighborhood_id(noble_sim_info) == kingdom_service.get_sim_neighborhood_id(target_sim_info)}")
        debug_log(f"Meets age requirement: {minimum_age.sequential_value <= target_sim_info.age.sequential_value}")
        debug_log(f"Lower noble rank: {lower_noble_rank}")

        return not headchild_rel < SETTINGS.minimum_rel_nobleinherit_threshold and not target_sim_info.is_dead and kingdom_service.get_sim_neighborhood_id(noble_sim_info) == kingdom_service.get_sim_neighborhood_id(target_sim_info) and minimum_age.sequential_value <= target_sim_info.age.sequential_value and lower_noble_rank

    def _meets_career_reqs(target_sim_info: SimInfo) -> bool:
        if target_sim_info is None:
            return False

        career_tracker = target_sim_info.career_tracker

        if career_tracker is None:
            return False

        has_work_career = False
        for career_uid, career in career_tracker.careers.items():
            if career.career_category == CareerCategory.Work:
                has_work_career = True
                break

        if SETTINGS.nobleinherit_career_req == "unemployedonly":
            if has_work_career:
                return False
        elif SETTINGS.nobleinherit_career_req == "priotisedunemployed":
            curr_inheriter_unemployed = noble_successor_sim_info is not None

            debug_log("NOBLE CAREER CHECKS")
            debug_log(f"Check sim: {target_sim_info.first_name} {target_sim_info.last_name}")
            debug_log(f"Sims has job: {has_work_career}")

            if curr_inheriter_unemployed:
                inheriter_career_tracker = noble_successor_sim_info.career_tracker

                if inheriter_career_tracker is not None:
                    for career_uid, career in inheriter_career_tracker.careers.items():
                        if career.career_category == CareerCategory.Work:
                            curr_inheriter_unemployed = False
                            break
            
                debug_log(f"Current chosen successor: {noble_successor_sim_info.first_name} {noble_successor_sim_info.last_name}")
                debug_log(f"Chosen successor has job: {not curr_inheriter_unemployed}")


            if curr_inheriter_unemployed:
                return False
            elif has_work_career and noble_successor_sim_info is not None:
                return False
        elif SETTINGS.nobleinherit_career_req == "all":
            if noble_successor_sim_info is not None:
                return False

        return True


    noble_dynasty = _get_sim_dynasty(noble_sim_info)
    
    noble_children_sim_infos = _order_relative_list(list(noble_sim_info.genealogy.get_children_sim_ids_gen()))

    # Checking dynasty heirs.                                
    if noble_dynasty is not None:
        if noble_dynasty.get_head_sim_info() == noble_sim_info:
            heir_sim_info = noble_dynasty.get_heir_sim_info()
            if heir_sim_info is not None:
                if (heir_sim_info in noble_children_sim_infos or heir_sim_info.id == noble_sim_info.spouse_sim_id) and _can_be_successor(heir_sim_info) and _meets_career_reqs(heir_sim_info):
                    noble_successor_sim_info = heir_sim_info

    # Checking children.                              
    for child_sim_info in noble_children_sim_infos:
        if _can_be_successor(child_sim_info) and _meets_career_reqs(child_sim_info):
            noble_successor_sim_info = child_sim_info

    # Checking spouses.
    if noble_successor_sim_info is None:
        noble_spouse_sim_id = noble_sim_info.spouse_sim_id
        
        if noble_spouse_sim_id is not None:
            noble_spouse_sim_info = services.sim_info_manager().get(noble_spouse_sim_id)

            if _can_be_successor(noble_spouse_sim_info) and _meets_career_reqs(noble_spouse_sim_info):
                noble_successor_sim_info = noble_spouse_sim_info

    # Setting as successor if a qualifying sim is found.
    if noble_successor_sim_info is not None:
        _set_sim_as_noble_successor(noble_sim_info,noble_successor_sim_info)

        
# Function Name: _calculate_dynasty_black_sheeps()
# Description: Calculates dynasty outcasts based on the relationship with the head.
# If a dynasty member has a -60% relationship or lower with the head sim, they will be outcasted in the dynasty.
# If an existing dynasty outcast has a +0% or more with the head sim, their outcast status will be revoked.
def _calculate_dynasty_black_sheeps(dynasty) -> None:
    if (SETTINGS.automatic_blacksheep_selection and SETTINGS.global_dynasty_mod_enabler) is not True:
        return

    head_sim_info = dynasty.get_head_sim_info()

    if head_sim_info is None:
        return

    if _is_dynasty_played(dynasty)  == True:
        return

    member_sim_ids = list(dynasty.get_members())

    for member_sim_id in member_sim_ids:
        member_sim_info = services.sim_info_manager().get(member_sim_id)
        if member_sim_info is None:
            continue
        
        if member_sim_id == dynasty.get_head_sim_id() or member_sim_id == dynasty.get_heir_sim_id():
            continue

        headmember_rel = head_sim_info.relationship_tracker.get_relationship_score(member_sim_id)

        is_black_sheep = member_sim_info.has_trait(DynastyTunables.BLACK_SHEEP_TRAIT)

        if is_black_sheep and (headmember_rel > SETTINGS.minimum_rel_removeblacksheep_threshold or Age(SETTINGS.outcast_minimum_age).sequential_value > member_sim_info.age.sequential_value):
            dynasty.set_black_sheep(member_sim_info,negate=True,update_client=True)
        elif not is_black_sheep and headmember_rel <= SETTINGS.maximum_rel_blacksheep_threshold and Age(SETTINGS.outcast_minimum_age).sequential_value <= member_sim_info.age.sequential_value:
            dynasty.set_black_sheep(member_sim_info,negate=False,update_client=True)


def _get_highest_prestige_dynasty(dynasty_a,dynasty_b) -> Dynasty:
    highest_dynasty = dynasty_a
    try:
        if highest_dynasty is not None and dynasty_b is not None:
            if dynasty_b.get_prestige_value() > highest_dynasty.get_prestige_value():
                highest_dynasty = dynasty_b
        elif dynasty_b is not None:
            highest_dynasty = dynasty_b
    except:
        return highest_dynasty
    return highest_dynasty


def _clean_multi_dynasty_sim(target_sim_id):
    highest_dynasty = services.dynasty_service().get_sim_dynasty(target_sim_id)
    dynasties_to_clean = []
    for dynasty in list(services.dynasty_service()._dynasties.values()):
        if dynasty is None or highest_dynasty is dynasty:
            continue 
        member_sim_ids = list(dynasty.get_members())
        if target_sim_id not in member_sim_ids:
            continue
        else:
            dynasties_to_clean.append(dynasty)
        if dynasty.get_head_sim_id() == target_sim_id:
            highest_dynasty = dynasty
            break
        highest_dynasty = _get_highest_prestige_dynasty(dynasty,highest_dynasty) if not _is_dynasty_played(highest_dynasty) or (_is_dynasty_played(highest_dynasty) and _is_dynasty_played(dynasty)) else highest_dynasty
    for dynasty in dynasties_to_clean:
        if dynasty is not highest_dynasty:
            dynasty.remove_member(target_sim_id,update_client=True)


# Function Name: _check_child_for_dynasties()
# Description: Once a new child is born or adopted, this checks their parents for dynasties. If the parent is a head/heir of their dynasty, the child may be added.
# If both parents are in different dynasties which they are head/heirs of, the child will be added to whichever dynasty has the highest prestige.
def _check_child_for_dynasties(sim_info) -> None:
    if (SETTINGS.add_dynasty_children in ("head","headheir","all") and SETTINGS.automatic_children_join and SETTINGS.global_dynasty_mod_enabler) is not True :
        return

    if sim_info is None:
        return
    
    if _get_sim_dynasty(sim_info) is not None or sim_info.is_young_adult_or_older:
        return
    
    sim_is_in_dynasty = _get_sim_dynasty(sim_info) is not None
    
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

        debug_log(f"Parent In Dynasty: {parent_dynasty is not None}")
        
        if parent_dynasty is None or _is_dynasty_played(parent_dynasty)  == True:
            continue

        debug_log(f"Parent Dynasty Name: {parent_dynasty.name}")
        debug_log(f"Parent Dynasty Prestige: {parent_dynasty.get_prestige_value()}")
        
        if SETTINGS.add_dynasty_children == "headheir":
            if parent_sim_id != parent_dynasty.get_head_sim_id() and parent_sim_id != parent_dynasty.get_heir_sim_id():
                continue
        elif SETTINGS.add_dynasty_children == "head":
            if parent_sim_id != parent_dynasty.get_head_sim_id():
                continue
        
        if highest_dynasty is None:
            highest_dynasty = parent_dynasty
        elif highest_dynasty is not None and parent_dynasty is not None and not _is_dynasty_played(highest_dynasty):
            if _is_dynasty_played(parent_dynasty) or _get_highest_prestige_dynasty(highest_dynasty,parent_dynasty) is parent_dynasty:
                highest_dynasty = parent_dynasty

    if highest_dynasty is not None:
        debug_log(f"Adding {sim_info.first_name} {sim_info.last_name} to {highest_dynasty.name} Dynasty.")
        highest_dynasty.add_member(sim_info,update_client=True)

        if SETTINGS.enforce_dynasty_name is True and sim_info.is_child_or_younger:
            for parent_sim_id in parent_sim_ids:
                parent_sim_info = services.sim_info_manager().get(parent_sim_id)
                if parent_sim_info is None:
                    continue
                if highest_dynasty is _get_sim_dynasty(parent_sim_info):
                    if parent_sim_info.last_name.split(' ')[0] == highest_dynasty.name:
                        sim_info.last_name = highest_dynasty.name
                        break


# Function Name: _on_sim_marriage()
# Description: Once a marriage occurs, this function checks if either/both sims are in a dynasty and are the head/heir.
# If only one side is a head/heir of a dynasty, the other member will be added.
# If both are heads/heirs of a dynasty, the sim from the lower prestige dynasty will join the higher one.
def _on_sim_marriage(sim_info,spouse_sim_info):
    if (SETTINGS.add_dynasty_spouse in ("head","headheir","all") and SETTINGS.automatic_spouse_join and SETTINGS.global_dynasty_mod_enabler) is not True:
        return
    
    sim_dynasty = _get_sim_dynasty(sim_info)
    spouse_dynasty = _get_sim_dynasty(spouse_sim_info)

    if _is_dynasty_played(sim_dynasty) == True or _is_dynasty_played(spouse_dynasty)  == True:
        return
        
    sim_is_head = False
    sim_is_heir = False
    spouse_is_head = False
    spouse_is_heir = False 

    debug_log("**AUTODYNASTYMOD SIM MARRIAGE CHECK**")
    debug_log(f"Sim Name: {sim_info.first_name} {sim_info.last_name}")
    debug_log(f"Spouse Name: {spouse_sim_info.first_name} {spouse_sim_info.last_name}")

    if sim_dynasty is not None:
        sim_is_head = sim_info == sim_dynasty.get_head_sim_info()
        sim_is_heir = sim_info == sim_dynasty.get_heir_sim_info()
        
    if spouse_dynasty is not None:
        spouse_is_head = spouse_sim_info == spouse_dynasty.get_head_sim_info()
        spouse_is_heir = spouse_sim_info == spouse_dynasty.get_heir_sim_info()

    debug_log(f"Sim Is Dynasty Head/Heir: {sim_is_head or sim_is_heir}")
    debug_log(f"Spouse Is Dynasty Head/Heir: {spouse_is_head or spouse_is_heir}")

    if spouse_dynasty is not sim_dynasty:
        if SETTINGS.add_dynasty_spouse == "head":
            if sim_is_head == False:
                sim_dynasty = None
            if spouse_is_head == False:
                spouse_dynasty = None
        elif SETTINGS.add_dynasty_spouse == "headheir":
            if (sim_is_head or sim_is_heir) == False:
                sim_dynasty = None
            if (spouse_is_head or spouse_is_heir) == False:
                spouse_dynasty = None
        
        highest_dynasty = _get_highest_prestige_dynasty(sim_dynasty,spouse_dynasty)
        
        if highest_dynasty is None:
            return

        if highest_dynasty == sim_dynasty:
            highest_dynasty.add_member(spouse_sim_info,update_client=True)
        else:
            highest_dynasty.add_member(sim_info,update_client=True)

        _sync_dynasty_names(sim_info,spouse_sim_info)

def _sync_dynasty_names(sim_info,spouse_sim_info,dynasty_save_data=None):
    if (SETTINGS.enforce_dynasty_name and SETTINGS.global_dynasty_mod_enabler) is not True:
        return

    if sim_info is None or spouse_sim_info is None:
        return

    dynasty = _get_sim_dynasty(sim_info)

    if dynasty is None or dynasty != _get_sim_dynasty(spouse_sim_info) or sim_info.last_name == spouse_sim_info.last_name or _is_dynasty_played(dynasty) == True:
        return

    dynasty_name = getattr(dynasty, "name", None)
    
    if not dynasty_name:
        return

    debug_log(f"**DYNASTY MARRIAGE NAME CHECK**")
    debug_log(f"Sim last name: {sim_info.last_name}")
    debug_log(f"Spouse last name: {spouse_sim_info.last_name}")
    debug_log(f"Dynasty name: {dynasty_name}")

    sim_has_dynasty_name = sim_info.last_name.split(' ')[0] == dynasty_name
    spouse_has_dynasty_name = spouse_sim_info.last_name.split(' ')[0] == dynasty_name

    debug_log(f"Sim has dynasty name: {sim_has_dynasty_name}")
    debug_log(f"Spouse has dynasty name: {spouse_has_dynasty_name}")
    
    if sim_has_dynasty_name != spouse_has_dynasty_name:
        if sim_has_dynasty_name:
            debug_log(f"Updating spouse's name")
            spouse_sim_info.last_name = dynasty_name
        elif spouse_has_dynasty_name:
            debug_log(f"Updating sim's name")
            sim_info.last_name = dynasty_name


# Function Name: _calculate_dynasty_relations()
# Description: Calculates the relations between different dynasties based on relations to the head or dynasty to a whole.
# To create a new alliance, a head sim must either be friends with the dynasty head or have a positive average relationship with the members. (the alliance must also be within the set level gap)
# To create a new rivalry, a head sim must have a poor relationship with another head sim or average across all members.
# To remove an existing alliance, a head sim must not have a positive relationship with another and must have a small or negative average relationship with all members.
# To remove an existing rivalry, a head sim must have a positive relationship with the other head sim.
def _calculate_dynasty_relations(main_dynasty: Dynasty) -> None:
    if (SETTINGS.global_dynasty_relations_enabler and SETTINGS.global_dynasty_mod_enabler) is not True:
        return

    dynasty_service = services.dynasty_service()
    sim_info_manager = services.sim_info_manager()

    main_head_sim_info = main_dynasty.get_head_sim_info()
    
    if main_head_sim_info is None or dynasty_service is None or sim_info_manager is None:
        return

    if _is_dynasty_played(main_dynasty) == True:
        return

    def _calculate_average_dynasty_rel(target_dynasty: Dynasty):
        rel_total = 0
        target_member_sim_ids = list(target_dynasty.get_members())

        for member_sim_id in target_member_sim_ids:
            if member_sim_id is None:
                continue
            rel_total += main_head_sim_info.relationship_tracker.get_relationship_score(member_sim_id)

        return rel_total / len(target_member_sim_ids)

    main_dynasty_prestige_level = main_dynasty.get_total_prestige_stat().rank_level

    debug_log(f"*DYNASTY RELATIONS CHECK*")
    debug_log(f"Dynasty name: {main_dynasty.name}")
    debug_log(f"Dynasty Prestige Level: {main_dynasty_prestige_level}")

    dynasty_allies = list(main_dynasty._alliances)

    if SETTINGS.automatic_remove_alliances == True:
        for ally_dynasty_id in dynasty_allies:
            ally_dynasty = dynasty_service.get_dynasty(ally_dynasty_id)

            if ally_dynasty is None or ally_dynasty == main_dynasty:
                continue

            ally_head_sim_info = ally_dynasty.get_head_sim_info()

            if ally_head_sim_info is None or _is_dynasty_played(ally_dynasty)  == True:
                continue

            if main_dynasty.is_rival(ally_dynasty):
                dynasty_service.end_rivalry(main_dynasty,ally_dynasty)

            ally_head_rel = main_head_sim_info.relationship_tracker.get_relationship_score(ally_head_sim_info.id)
            ally_average_rel = _calculate_average_dynasty_rel(ally_dynasty)

            debug_log(f"Ally Dynasty name: {ally_dynasty.name}")
            debug_log(f"Ally Head Relationship: {ally_head_rel}")
            debug_log(f"Ally Average Relationship: {ally_average_rel}")

            if (ally_head_rel <= SETTINGS.maximum_head_rel_remove_ally and ally_average_rel <= SETTINGS.maximum_average_rel_remove_ally):
                debug_log(f"Removing {ally_dynasty.name} as {main_dynasty.name} ally.")
                dynasty_service.end_alliance(main_dynasty,ally_dynasty)

    dynasty_rivals = list(main_dynasty._rivalries)

    if SETTINGS.automatic_remove_rivalries == True:
        for rival_dynasty_id in dynasty_rivals:
            rival_dynasty = dynasty_service.get_dynasty(rival_dynasty_id)

            if rival_dynasty is None or rival_dynasty == main_dynasty:
                continue

            rival_head_sim_info = rival_dynasty.get_head_sim_info()

            if rival_head_sim_info is None or _is_dynasty_played(rival_dynasty)  == True:
                continue
            
            rival_head_rel = main_head_sim_info.relationship_tracker.get_relationship_score(rival_head_sim_info.id)

            debug_log(f"Rival Dynasty name: {rival_dynasty.name}")
            debug_log(f"Rival Head Relationship: {rival_head_rel}")
            
            if rival_head_rel >= SETTINGS.minimum_head_rel_remove_rival:
                debug_log(f"Removing {rival_dynasty.name} as {main_dynasty.name} rival.")
                dynasty_service.end_rivalry(main_dynasty,rival_dynasty)

    all_dynasties = dynasty_service.get_all_dynasties()
    
    for target_dynasty in all_dynasties.values():
        if target_dynasty is None:
            continue
        elif target_dynasty == main_dynasty or main_dynasty.is_ally(target_dynasty) or main_dynasty.is_rival(target_dynasty) or _is_dynasty_played(target_dynasty)  == True:
            continue

        target_head_sim_info = target_dynasty.get_head_sim_info()

        if target_head_sim_info is None:
            continue

        target_head_rel = main_head_sim_info.relationship_tracker.get_relationship_score(target_head_sim_info.id)
        target_average_rel = _calculate_average_dynasty_rel(target_dynasty)

        target_dynasty_prestige_level = main_dynasty.get_total_prestige_stat().rank_level

        debug_log(f"Target Dynasty name: {target_dynasty.name}")
        debug_log(f"Target Head Relationship: {target_head_rel}")
        debug_log(f"Target Average Relationship: {target_average_rel}")
        debug_log(f"Target Prestige Level: {target_dynasty_prestige_level}")

        if (target_head_rel >= SETTINGS.minimum_head_rel_new_ally or target_average_rel >= SETTINGS.minimum_average_rel_new_ally) and SETTINGS.automatic_alliances == True and target_dynasty_prestige_level in range(main_dynasty_prestige_level - SETTINGS.maximum_level_gap_new_ally, main_dynasty_prestige_level + SETTINGS.maximum_level_gap_new_ally):
            debug_log(f"Adding {target_dynasty.name} as {main_dynasty.name} ally.")
            dynasty_service.add_alliance(main_dynasty,target_dynasty)
        elif (target_head_rel <= SETTINGS.maximum_head_rel_new_rival or target_average_rel <= SETTINGS.maximum_average_rel_new_rival) and SETTINGS.automatic_rivalries == True:
            debug_log(f"Adding {target_dynasty.name} as {main_dynasty.name} rival.")
            dynasty_service.add_rivalry(main_dynasty,target_dynasty)

def _offspring_repair_check(update_kingdom_titles=False):
    repaired = 0
    sim_info_manager = services.sim_info_manager()
    if sim_info_manager is None:
        logger.error('DynastyService: sim_info_manager is None, skipping offspring repair.')
        return 0
    dynasty_service = services.dynasty_service()
    kingdom_service = services.kingdom_service()
    for child_sim_info in sim_info_manager.get_all():
        if not child_sim_info is None:
            if not child_sim_info.is_pet:
                if dynasty_service.get_sim_dynasty(child_sim_info.id) is None:
                    if (child_sim_info.household.is_player_household and SETTINGS.enable_repair_for_played) or (not child_sim_info.household.is_player_household and SETTINGS.enable_repair_for_unplayed):
                        dynasty = _calculate_sim_for_dynasty(child_sim_info)
                        if dynasty is not None:
                            debug_log(f"SELECTED {dynasty.name} DYNASTY FOR {child_sim_info.first_name} {child_sim_info.last_name}")
                            dynasty.add_member(child_sim_info)
                            if update_kingdom_titles and kingdom_service is not None:
                                kingdom_service.update_sim_info_title(child_sim_info)
                            repaired += 1
    return repaired

def _on_daily_update(owner):
    global daily_check_alarm_handle
    now = services.time_service().sim_now

    debug_log(f"HOUR NUMBER: {now.hour()}")
    debug_log(f"DAY NUMBER: {now.day()}")

    if SETTINGS.enable_daily_updates:
        if now.day() in SETTINGS.daily_update_days:
            try:
                sim_info_manager = services.sim_info_manager()
                for (dynasty_id, dynasty) in services.dynasty_service()._dynasties.items():
                    if dynasty and _is_dynasty_played(dynasty) is False:
                        _calculate_dynasty_heir(dynasty)
                        _calculate_dynasty_black_sheeps(dynasty)
                        _calculate_dynasty_relations(dynasty)

                        member_sim_ids = list(dynasty.get_members())
                        for member_sim_id in member_sim_ids:
                            member_sim_info = sim_info_manager.get(member_sim_id)
                            if member_sim_info:
                                member_children_sim_infos = _order_relative_list(list(member_sim_info.genealogy.get_children_sim_ids_gen()))
                                for child_sim_info in member_children_sim_infos:
                                    if _get_sim_dynasty(child_sim_info) is None and not child_sim_info.household.is_player_household:
                                        _check_child_for_dynasties(child_sim_info)
                                spouse_sim_info = sim_info_manager.get(member_sim_info.spouse_sim_id)
                                if spouse_sim_info is not None:
                                    if dynasty is not _get_sim_dynasty(spouse_sim_info):
                                        _on_sim_marriage(member_sim_info,spouse_sim_info)
                                    else:
                                        if member_sim_info.last_name != spouse_sim_info.last_name:
                                            _sync_dynasty_names(member_sim_info,spouse_sim_info)
                if SETTINGS.daily_ea_repair:
                    _offspring_repair_check(update_kingdom_titles=True)
            except:
                debug_log("EXCEPTION in daily dynasty update:\n" + traceback.format_exc())
    else:
        _clear_alarm()

def _add_alarm(owner):
    if SETTINGS.enable_daily_updates:
        debug_log("ALARM SET")
        now = services.time_service().sim_now
        update_time = date_and_time.create_date_and_time(
            hours=SETTINGS.daily_update_time
        )
        time_until_first_alarm = now.time_till_next_day_time(update_time)
        return alarms.add_alarm(owner, time_until_first_alarm, _on_daily_update, repeating=True, repeating_time_span=date_and_time.create_time_span(days=1))

def _clear_alarm():
    global daily_check_alarm_handle 
    if daily_check_alarm_handle is not None:
        alarms.cancel_alarm(daily_check_alarm_handle)
        daily_check_alarm_handle = None

def _reset_alarm():
    _clear_alarm()
    _add_alarm(owner=services.dynasty_service())

# *Hooks*

@inject_to(DynastyService, "_repair_existing_children_for_dynasties")
def _hook_dynastyservice_repair_existing_children_for_dynastiest(original, self, update_kingdom_titles, *args, **kwargs):
    if not SETTINGS.global_automatic_repair:
        return 0
    repaired = _offspring_repair_check(update_kingdom_titles)
    return repaired


@inject_to(DynastyService, "handle_new_child_event")
def _hook_dynastyservice_handle_new_child_event(original, self, parent_sim_info, offspring_sim_info, *args, **kwargs):
    try:
        if offspring_sim_info is None or offspring_sim_info.is_pet or _get_sim_dynasty(offspring_sim_info) is not None:
            return
        if not offspring_sim_info.household.is_player_household or (SETTINGS.global_automatic_repair and SETTINGS.enable_repair_for_played):
            _check_child_for_dynasties(offspring_sim_info)
    except:
        return original(self, parent_sim_info, offspring_sim_info, *args, **kwargs)


@inject_to(DynastyService, "_on_sim_spawned")
def _hook_dynasty_service_on_sim_spawned(original, self, *args, **kwargs):
    debug_log("HOOK: DynastyService._on_sim_spawned fired")
    result = original(self, *args, **kwargs)
    try:
        for (dynasty_id, dynasty) in self._dynasties.items():
            if dynasty is not None and _is_dynasty_played(dynasty) is not True:
                member_sim_ids = list(dynasty.get_members())
                for member_sim_id in member_sim_ids:
                    member_sim_info = services.sim_info_manager().get(member_sim_id)
                    if member_sim_info:
                        spouse_sim_info = services.sim_info_manager().get(member_sim_info.spouse_sim_id)
                        if spouse_sim_info is not None:
                            if dynasty is _get_sim_dynasty(spouse_sim_info):
                                if member_sim_info.last_name != spouse_sim_info.last_name:
                                    _sync_dynasty_names(member_sim_info,spouse_sim_info)
    except:
        debug_log("EXCEPTION in DynastyService._on_sim_spawned hook:\n" + traceback.format_exc())
    return result


# Runs when a new relationship bit is added between two sims.
# This is used to detect when a marriage happens or when two sims of the same dynasty have a relationship change.
# This allows for dynasty hierarchies to change with NPC dynasty member relationship changes. (such as heirs changing or members being outcasted)
# This too, also allows for noble successors to be changed.
@inject_to(RelationshipTracker, "add_relationship_bit")
def _hook_relationship_tracker_add_relationship_bit(original, self, target_sim_id, bit, *args, **kwargs):
    result = original(self, target_sim_id, bit, *args, **kwargs)
    try:
        kingdom_service = services.kingdom_service()
        
        sim_info = self._sim_info
        target_sim_info = services.sim_info_manager().get(target_sim_id)
        
        if sim_info is not None and target_sim_info is not None:
            sim_dynasty = _get_sim_dynasty(sim_info)
            target_dynasty = _get_sim_dynasty(target_sim_info)
            if sim_dynasty is not None:
                if sim_dynasty is target_dynasty:
                    _calculate_dynasty_heir(sim_dynasty)
                    _calculate_dynasty_black_sheeps(sim_dynasty)
                elif target_dynasty is not None:
                    _calculate_dynasty_relations(sim_dynasty)

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
def _hook_dynasty_add_member(original, self, sim_info, *args, **kwargs):
    debug_log("HOOK: Dynasty.add_member fired")
    result = original(self, sim_info, *args, **kwargs)
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
    
    if _is_dynasty_played(self)  == True:
        return result

    try:
        _calculate_dynasty_heir(self)
        _calculate_dynasty_black_sheeps(self)
    except:
        debug_log("EXCEPTION in Dynasty.remove_member hook:\n" + traceback.format_exc())
    return result


# Runs when a new head sim is set.
# Used to add existing children not yet part of the dynasty.
@inject_to(Dynasty, "set_head")
def _hook_dynasty_set_head(original, self, *args, **kwargs):
    debug_log("HOOK: Dynasty.set_head fired")
    result = original(self, *args, **kwargs)

    if _is_dynasty_played(self)  == True:
        return result
    
    try:
        head_sim_info = self.get_head_sim_info()

        if head_sim_info is None:
            return result

        head_children_sim_infos = _order_relative_list(list(head_sim_info.genealogy.get_children_sim_ids_gen()))

        if SETTINGS.automatic_children_join:
            for child_sim_info in head_children_sim_infos:
                if _get_sim_dynasty(child_sim_info) is None and child_sim_info is not None and _get_sim_dynasty(child_sim_info) == None:
                    self.add_member(child_sim_info,update_client=True)

        _calculate_dynasty_heir(self)
        _calculate_dynasty_black_sheeps(self)
    except:
        debug_log("EXCEPTION in Dynasty.set_head hook:\n" + traceback.format_exc())
    return result


# Runs after a noble sim with an inheriting sim dies.
# Sets up the sim to become a valid target for inheritance.
# Removes the sim's existing career and gives them the noble career if they live in the same neighbourhood, aren't dead and are at least a teenager.
# This should fulfil the requirements needed for EA to process the inheriting sim after this hook so that they inherit the noble rank.
@inject_to(KingdomService, "process_inheriting_sim")
def _hook_kingdomservice_process_inhertiing_sim(original, self, neighborhood_id, noble_sim_info, inheriting_sim_id, *args, **kwargs):
    debug_log("HOOK: KingdomService.process_inheriting_sim fired")
    try:
        if SETTINGS.global_noble_mod_enabler != True:
            return

        if neighborhood_id is not None:
            debug_log("**NOBLE DEATH**")
            debug_log(f"Noble Sim Name: {noble_sim_info.first_name} {noble_sim_info.last_name}")
            
            inheriting_sim_info = services.sim_info_manager().get(inheriting_sim_id)

            if inheriting_sim_info is not None:
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
        if dying_sim_info is not None:
            debug_log("**SIM ABOUT TO DIE**")
            debug_log(f"Dying Sim Name: {dying_sim_info.first_name} {dying_sim_info.last_name}")

            is_noble = kingdom_service.has_noble_career(dying_sim_info)

            debug_log(f"Is Noble: {is_noble}")
            
            if dying_sim_info.household.is_player_household is not True and is_noble == True:
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

        if sim_info is not None:
            is_noble = kingdom_service.has_noble_career(sim_info)

            if sim_info.household.is_player_household != True and is_noble == True:
                debug_log("**NOBLE SIM JOINED CAREER**")
                debug_log(f"Sim Name: {sim_info.first_name} {sim_info.last_name}")
                _calculate_noble_successor(sim_info)
    except:
        debug_log("EXCEPTION in CareerTracker.add_career hook:\n" + traceback.format_exc())
        
    return result

# Runs when the spouse event if fired.
# Used to detect marriages to add spouses to dynasties as appropriate.
@inject_to(KingdomService, "handle_spouse_event")
def _hook_kingdom_service_handle_spouse_eventr(original, self, sim_info, resolver, *args, **kwargs):
    debug_log("HOOK: KingdomService.handle_spouse_event fired")
    result = original(self, sim_info, resolver, *args, **kwargs)
    try:
        kingdom_service = services.kingdom_service()

        debug_log("KINGDOM SERVICE SPOUSE EVENT")
        debug_log(f"Sim: {sim_info.first_name} {sim_info.last_name}")
        spouse_sim_id = resolver.event_kwargs['spouse_sim_id']
        ex_spouse_sim_id = resolver.event_kwargs['ex_spouse_sim_id']
        spouse_sim_info = services.sim_info_manager().get(spouse_sim_id) if spouse_sim_id else services.sim_info_manager().get(ex_spouse_sim_id)
        debug_log(f"Spouse Sim: {spouse_sim_info.first_name} {spouse_sim_info.last_name}")
        _on_sim_marriage(sim_info,spouse_sim_info)
    except:
        debug_log("EXCEPTION in KingdomService.handle_spouse_event hook:\n" + traceback.format_exc())
        
    return result


@inject_to(DynastyService, "on_all_households_and_sim_infos_loaded")
def _hook_dynastyservice_on_all_households_and_sim_infos_loaded(original, self, client, *args, **kwargs):
    try:
        distributor_op = DistributorOps_pb2.DynastyInfo()
        distributor_op.message_type = DynastyMessageType.ADD
        active_household = services.active_household()
        dynasties_to_remove = []
        for (dynasty_id, dynasty) in self._dynasties.items():
            try:
                dynasty.on_all_households_and_sim_infos_loaded(active_household)
                if len(dynasty.get_members()) == 0:
                    dynasties_to_remove.append(dynasty)
                else:
                    sim_info_manager = services.sim_info_manager()
                    with ProtocolBufferRollback(distributor_op.dynasties) as dynasty_data_msg:
                        dynasty.add_dynasty_members(dynasty_data_msg, sim_info_manager)
                        dynasty.add_detailed_dynasty_data(dynasty_data_msg, sim_info_manager)
            except:
                logger.exception('Unhandled error in on_all_households_and_sim_infos_loaded of dynasty: {}', dynasty_id)
        for dynasty in dynasties_to_remove:
            self.remove_dynasty(dynasty)
        if not self._offspring_repair_done:
            repaired = self._repair_existing_children_for_dynasties(update_kingdom_titles=True)
            logger.info('DynastyService: offspring repair added %s sims', repaired)
            self._offspring_repair_done = True
        for (dynasty_id, dynasty) in list(self._dynasties.items()):
            member_sim_ids = list(dynasty.get_members())
            for member_sim_id in member_sim_ids:
                if self.get_sim_dynasty(member_sim_id) is not dynasty:
                    _clean_multi_dynasty_sim(member_sim_id)
            dynasty.distribute_dynasty_msg(DynastyMessageType.UPDATE)
        self.send_dynasties_to_client(distributor_op)
    except:
        debug_log("EXCEPTION in DynastyService.on_all_households_and_sim_infos_loaded hook:\n" + traceback.format_exc())
        return original(self, client, *args, **kwargs)
    return

@inject_to(DynastyService, "on_zone_load")
def _hook_dynastyservice_on_zone_load(original, self, *args, **kwargs):
    debug_log("HOOK: DynastyService.on_zone_load fired")
    result = original(self, *args, **kwargs)
    try:
        global daily_check_alarm_handle 
        _clear_alarm()
        daily_check_alarm_handle = _add_alarm(self)
    except:
        debug_log("EXCEPTION in DynastyService.on_zone_load hook:\n" + traceback.format_exc())
    return result

@inject_to(DynastyService, "on_zone_unload")
def _hook_dynastyservice_on_zone_unload(original, self, *args, **kwargs):
    debug_log("HOOK: DynastyService.on_zone_unload fired")
    result = original(self, *args, **kwargs)
    try:
        _clear_alarm()
    except:
        debug_log("EXCEPTION in DynastyService.on_zone_unload hook:\n" + traceback.format_exc())
    return result