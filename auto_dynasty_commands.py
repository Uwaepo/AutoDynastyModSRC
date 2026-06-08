# *Python Modules*
import traceback

# *Sims 4 Modules*
import sims4.commands
from server_commands.argument_helpers import OptionalSimInfoParam, get_optional_target
from sims.sim_info_types import Age

from relationships.relationship_enums import RelationshipType

from .ui.auto_dynasty_uidialogs import show_text_input_dialog, show_item_picker_dialog
from .utils.debug_logger import debug_log

# *My Modules*
from .auto_dynasty_menus import push_sa, show_main_settings_picker, show_dynasty_settings_picker, show_noble_settings_picker, show_enable_disable_setting_picker, show_number_setting_picker, show_item_setting_picker, show_dynastychild_settings_picker, show_dynastymarriage_settings_picker, show_dynastyheir_settings_picker, show_dynastyblacksheep_settings_picker, show_dynastyrelations_settings_picker, show_dynastyrelations_alliances_picker, show_dynastyrelations_rivalries_picker, show_earepair_settings_picker, SELECTED_ICON, UNSELECTED_ICON, GO_BACK_ICON
from .auto_dynasty_settings import SETTINGS
from .auto_dynasty_tuning import MOD_SA_IDS

@sims4.commands.Command(
    'uwaepo.dynastymod_open_menu',
    command_type=sims4.commands.CommandType.Live
)
def dynasty_open_item_picker_menu(menu_name: str = "", opt_sim: OptionalSimInfoParam = None, _connection=None):
    debug_log("COMMMAND: uwaepo.dynastymod_open_menu fired")
    try:
        sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
        if sim_info is None:
            debug_log("[AutoDynastyMod] No SimInfo found.", _connection)
            return False
        
        if menu_name == "main":
            show_main_settings_picker(sim_info)
        elif menu_name == "dynasty":
            show_dynasty_settings_picker(sim_info)
        elif menu_name == "dynasty_children":
            show_dynastychild_settings_picker(sim_info)
        elif menu_name == "dynasty_marriage":
            show_dynastymarriage_settings_picker(sim_info)
        elif menu_name == "dynasty_heir":
            show_dynastyheir_settings_picker(sim_info)
        elif menu_name == "dynasty_outcast":
            show_dynastyblacksheep_settings_picker(sim_info)
        elif menu_name == "noble":
            show_noble_settings_picker(sim_info)
        elif menu_name == "relations":
            show_dynastyrelations_settings_picker(sim_info)
        elif menu_name == "alliances":
            show_dynastyrelations_alliances_picker(sim_info)
        elif menu_name == "rivalries":
            show_dynastyrelations_rivalries_picker(sim_info)
        elif menu_name == "earepair":
            show_earepair_settings_picker(sim_info)
    except:
        debug_log("EXCEPTION in uwaepo.dynastymod_open_menu command:\n" + traceback.format_exc())

@sims4.commands.Command(
    'uwaepo.dynastymod_open_settings_enabledisabler_picker',
    command_type=sims4.commands.CommandType.Live
)
def dynasty_open_settings_enabledisabler_picker(setting_name: str = "", sa_key: str = "", parent_sa_key: str = "", title_key: str = "", text_key: str = "", opt_sim: OptionalSimInfoParam = None, _connection=None):
    debug_log("COMMMAND: uwaepo.dynastymod_open_settings_enabledisabler_picker fired")
    try:
        sa_id = MOD_SA_IDS.get(sa_key)
        parent_sa_id = MOD_SA_IDS.get(parent_sa_key)

        try:
            title_key = int(title_key,0)
            text_key = int(text_key,0)
        except ValueError:
            return

        if (sa_id is not None and parent_sa_id is not None):

            sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
            if sim_info is None:
                debug_log("[AutoDynastyMod] No SimInfo found.", _connection)
                return False
            
            show_enable_disable_setting_picker(sim_info,setting_name,sa_id,parent_sa_id,title_key,text_key)
    except:
        debug_log("EXCEPTION in uwaepo.dynastymod_open_settings_enabledisabler_picker command:\n" + traceback.format_exc())


@sims4.commands.Command(
    'uwaepo.dynastymod_open_settings_number_picker',
    command_type=sims4.commands.CommandType.Live
)
def dynasty_open_settings_number_picker(setting_name: str = "", parent_sa_key: str = "", lower_bound: int = -100, upper_bound: int = 100, title_key: str = "", text_key: str = "", field_title_key: str = "", opt_sim: OptionalSimInfoParam = None, _connection=None):
    debug_log("COMMMAND: uwaepo.dynastymod_open_settings_number_picker fired")
    try:
        parent_sa_id = MOD_SA_IDS.get(parent_sa_key)

        try:
            title_key = int(title_key,0)
            text_key = int(text_key,0)
            field_title_key = int(field_title_key,0)
        except ValueError:
            return

        if (parent_sa_id is not None):

            sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
            if sim_info is None:
                debug_log("[AutoDynastyMod] No SimInfo found.", _connection)
                return False
            
            show_number_setting_picker(sim_info=sim_info,setting_name=setting_name,parent_sa_id=parent_sa_id,lower_bound=lower_bound,upper_bound=upper_bound,title_key=title_key,text_key=text_key,field_title_key=field_title_key)
    except:
        debug_log("EXCEPTION in uwaepo.dynastymod_open_settings_number_picker command:\n" + traceback.format_exc())


@sims4.commands.Command(
    'uwaepo.dynastymod_open_settings_headheirmember_picker',
    command_type=sims4.commands.CommandType.Live
)
def dynasty_open_settings_headheirmember_picker(setting_name: str = "", sa_key: str = "", parent_sa_key: str = "", title_key: str = "", text_key: str = "", opt_sim: OptionalSimInfoParam = None, _connection=None):
    debug_log("COMMMAND: uwaepo.dynastymod_open_settings_headheirmember_picker fired")
    try:
        sa_id = MOD_SA_IDS.get(sa_key)
        parent_sa_id = MOD_SA_IDS.get(parent_sa_key)

        try:
            title_key = int(title_key,0)
            text_key = int(text_key,0)
        except ValueError:
            return

        sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
        if sim_info is None:
            debug_log("[AutoDynastyMod] No SimInfo found.", _connection)
            return False

        sim = sim_info.get_sim_instance()
    
        if not sim:
            return

        if (sa_id is not None and parent_sa_id is not None):

            def on_setting_change(dialog_instance):
                if not dialog_instance.accepted:
                    push_sa(sim,parent_sa_id)
                    return

                result_tag = dialog_instance.get_single_result_tag()
                debug_log(f"PICKER RESULT: {result_tag}")

                new_setting = result_tag
                        
                if result_tag == "goback":
                    push_sa(sim,parent_sa_id)
                    return

                if new_setting is not None:
                    debug_log(f"CHANGING SETTING")
                    setattr(SETTINGS,setting_name,new_setting)
                    SETTINGS.save()
                push_sa(sim,sa_id)

            rows=[
                {
                    "name_key": 0xC9797023, # Head Sim Only
                    "tag": "head",
                    "is_enable": True,
                    "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == "head" else UNSELECTED_ICON
                },
                {
                    "name_key": 0x78EDEC34, # Head and Heir Sims Only
                    "tag": "headheir",
                    "is_enable": True,
                    "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == "headheir" else UNSELECTED_ICON
                },
                {
                    "name_key": 0x49BCD0FB, # All Dynasty Members
                    "tag": "all",
                    "is_enable": True,
                    "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == "all" else UNSELECTED_ICON
                },
                {
                    "name_key": 0xDDC3EC7E, # Go back
                    "tag": "goback",
                    "is_enable": True,
                    "icon": GO_BACK_ICON
                }
            ]
            
            show_item_setting_picker(sim_info,rows,on_setting_change,title_key,text_key)
    except:
        debug_log("EXCEPTION in uwaepo.dynastymod_open_settings_headheirmember_picker command:\n" + traceback.format_exc())


@sims4.commands.Command(
    'uwaepo.dynastymod_open_settings_dynastyfamilialrelation_picker',
    command_type=sims4.commands.CommandType.Live
)
def dynasty_open_settings_dynastyfamilialrelation_picker(setting_name: str = "", sa_key: str = "", parent_sa_key: str = "", title_key: str = "", text_key: str = "", opt_sim: OptionalSimInfoParam = None, _connection=None):
    debug_log("COMMMAND: uwaepo.dynasty_open_settings_dynastyfamilialrelation_picker fired")
    try:
        sa_id = MOD_SA_IDS.get(sa_key)
        parent_sa_id = MOD_SA_IDS.get(parent_sa_key)

        try:
            title_key = int(title_key,0)
            text_key = int(text_key,0)
        except ValueError:
            return

        sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
        if sim_info is None:
            debug_log("[AutoDynastyMod] No SimInfo found.", _connection)
            return False

        sim = sim_info.get_sim_instance()
    
        if not sim:
            return

        if (sa_id is not None or parent_sa_id is not None):

            def on_setting_change(dialog_instance):
                if not dialog_instance.accepted:
                    push_sa(sim,parent_sa_id)
                    return

                result_tags = dialog_instance.get_result_tags()

                if "goback" in result_tags:
                    push_sa(sim,parent_sa_id)
                    return
                    
                new_setting = getattr(SETTINGS,setting_name,[])
                
                for tag in result_tags:
                    if tag in new_setting:
                        new_setting.remove(tag)
                    else:
                        new_setting.append(tag)

                if new_setting is not None:
                    debug_log(f"CHANGING SETTING")
                    setattr(SETTINGS,setting_name,new_setting)
                    SETTINGS.save()
                
                push_sa(sim,sa_id)
            
            rows=[
                {
                    "name_key": 0xCB5E673E, # Children
                    "tag": "children",
                    "is_enable": True,
                    "icon": SELECTED_ICON if "children" in getattr(SETTINGS,setting_name,None) else UNSELECTED_ICON
                },
                {
                    "name_key": 0x7FDD62ED, # Spouses
                    "tag": "spouse",
                    "is_enable": True,
                    "icon": SELECTED_ICON if "spouse" in getattr(SETTINGS,setting_name,None) else UNSELECTED_ICON
                },
                {
                    "name_key": 0x6E6E8B3A, # Siblings
                    "tag": "siblings",
                    "is_enable": True,
                    "icon": SELECTED_ICON if "siblings" in getattr(SETTINGS,setting_name,None) else UNSELECTED_ICON
                },
                {
                    "name_key": 0xF403E269, # Parents
                    "tag": "parents",
                    "is_enable": True,
                    "icon": SELECTED_ICON if "parents" in getattr(SETTINGS,setting_name,None) else UNSELECTED_ICON
                },
                {
                    "name_key": 0xDDC3EC7E, # Go back
                    "tag": "goback",
                    "is_enable": True,
                    "icon": GO_BACK_ICON
                }
            ]
            
            show_item_setting_picker(sim_info,rows,on_setting_change,title_key,text_key)
    except:
        debug_log("EXCEPTION in uwaepo.dynasty_open_settings_dynastyfamilialrelation_picker command:\n" + traceback.format_exc())


@sims4.commands.Command(
    'uwaepo.dynastymod_open_settings_heirgenderpriority_picker',
    command_type=sims4.commands.CommandType.Live
)
def dynasty_open_settings_heirgenderpriority_picker(setting_name: str = "", sa_key: str = "", parent_sa_key: str = "", title_key: str = "", text_key: str = "", opt_sim: OptionalSimInfoParam = None, _connection=None):
    debug_log("COMMMAND: uwaepo.dynasty_open_settings_heirgenderpriority_picker fired")
    try:
        sa_id = MOD_SA_IDS.get(sa_key)
        parent_sa_id = MOD_SA_IDS.get(parent_sa_key)

        try:
            title_key = int(title_key,0)
            text_key = int(text_key,0)
        except ValueError:
            return

        sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
        if sim_info is None:
            debug_log("[AutoDynastyMod] No SimInfo found.", _connection)
            return False

        sim = sim_info.get_sim_instance()
    
        if not sim:
            return

        if (sa_id is not None and parent_sa_id is not None):

            def on_setting_change(dialog_instance):
                if not dialog_instance.accepted:
                    push_sa(sim,parent_sa_id)
                    return

                result_tag = dialog_instance.get_single_result_tag()
                debug_log(f"PICKER RESULT: {result_tag}")

                new_setting = result_tag
                        
                if result_tag == "goback":
                    push_sa(sim,parent_sa_id)
                    return

                if new_setting is not None:
                    debug_log(f"CHANGING SETTING")
                    setattr(SETTINGS,setting_name,new_setting)
                    SETTINGS.save()
                push_sa(sim,sa_id)

            rows=[
                {
                    "name_key": 0xEE0C505F, # Male
                    "tag": "MALE",
                    "is_enable": True,
                    "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == "MALE" else UNSELECTED_ICON
                },
                {
                    "name_key": 0x15E5C270, # Female
                    "tag": "FEMALE",
                    "is_enable": True,
                    "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == "FEMALE" else UNSELECTED_ICON
                },
                {
                    "name_key": 0xAA369120, # None
                    "tag": "none",
                    "is_enable": True,
                    "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == "none" else UNSELECTED_ICON
                },
                {
                    "name_key": 0xDDC3EC7E, # Go back
                    "tag": "goback",
                    "is_enable": True,
                    "icon": GO_BACK_ICON
                }
            ]
            
            show_item_setting_picker(sim_info,rows,on_setting_change,title_key,text_key)
    except:
        debug_log("EXCEPTION in uwaepo.dynasty_open_settings_heirgenderpriority_picker command:\n" + traceback.format_exc())


@sims4.commands.Command(
    'uwaepo.dynastymod_open_settings_singleage_picker',
    command_type=sims4.commands.CommandType.Live
)
def dynasty_open_settings_singleage_picker(setting_name: str = "", sa_key: str = "", parent_sa_key: str = "", title_key: str = "", text_key: str = "", opt_sim: OptionalSimInfoParam = None, _connection=None):
    debug_log("COMMMAND: uwaepo.dynasty_open_settings_singleage_picker fired")
    try:
        sa_id = MOD_SA_IDS.get(sa_key)
        parent_sa_id = MOD_SA_IDS.get(parent_sa_key)

        try:
            title_key = int(title_key,0)
            text_key = int(text_key,0)
        except ValueError:
            return

        sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
        if sim_info is None:
            debug_log("[AutoDynastyMod] No SimInfo found.", _connection)
            return False

        sim = sim_info.get_sim_instance()
    
        if not sim:
            return

        if (sa_id is not None and parent_sa_id is not None):

            def on_setting_change(dialog_instance):
                if not dialog_instance.accepted:
                    push_sa(sim,parent_sa_id)
                    return

                result_tag = dialog_instance.get_single_result_tag()
                debug_log(f"PICKER RESULT: {result_tag}")

                new_setting = result_tag
                        
                if result_tag == "goback":
                    push_sa(sim,parent_sa_id)
                    return

                if new_setting is not None:
                    debug_log(f"CHANGING SETTING")
                    setattr(SETTINGS,setting_name,new_setting)
                    SETTINGS.save()
                push_sa(sim,sa_id)

            rows=[
                {
                    "name_key": 0x71AA5750, # Baby
                    "tag": "BABY",
                    "is_enable": True,
                    "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == "BABY" else UNSELECTED_ICON
                },
                {
                    "name_key": 0xADDA7C5E, # Infant
                    "tag": "INFANT",
                    "is_enable": True,
                    "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == "INFANT" else UNSELECTED_ICON
                },
                {
                    "name_key": 0xC131542D, # Toddler
                    "tag": "TODDLER",
                    "is_enable": True,
                    "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == "TODDLER" else UNSELECTED_ICON
                },
                {
                    "name_key": 0x2135D048, # Child
                    "tag": "CHILD",
                    "is_enable": True,
                    "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == "CHILD" else UNSELECTED_ICON
                },
                {
                    "name_key": 0x9F66F27C, # Teen
                    "tag": "TEEN",
                    "is_enable": True,
                    "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == "TEEN" else UNSELECTED_ICON
                },
                {
                    "name_key": 0xD2DC11B3, # Young Adult
                    "tag": "YOUNGADULT",
                    "is_enable": True,
                    "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == "YOUNGADULT" else UNSELECTED_ICON
                },
                {
                    "name_key": 0xF54C0CD8, # Adult
                    "tag": "ADULT",
                    "is_enable": True,
                    "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == "ADULT" else UNSELECTED_ICON
                },
                {
                    "name_key": 0x0C48C339, # Elder
                    "tag": "ELDER",
                    "is_enable": True,
                    "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == "ELDER" else UNSELECTED_ICON
                },
                {
                    "name_key": 0xDDC3EC7E, # Go back
                    "tag": "goback",
                    "is_enable": True,
                    "icon": GO_BACK_ICON
                }
            ]
            
            show_item_setting_picker(sim_info,rows,on_setting_change,title_key,text_key)
    except:
        debug_log("EXCEPTION in uwaepo.dynasty_open_settings_singleage_picker command:\n" + traceback.format_exc())


@sims4.commands.Command(
    'uwaepo.dynastymod_open_settings_singleage_minage_picker',
    command_type=sims4.commands.CommandType.Live
)
def dynasty_open_settings_singleage_minage_picker(setting_name: str = "", sa_key: str = "", parent_sa_key: str = "", minimum_age_name: str = "BABY", title_key: str = "", text_key: str = "", opt_sim: OptionalSimInfoParam = None, _connection=None):
    debug_log("COMMMAND: uwaepo.dynasty_open_settings_singleage_minage_picker fired")
    try:
        sa_id = MOD_SA_IDS.get(sa_key)
        parent_sa_id = MOD_SA_IDS.get(parent_sa_key)

        minimum_age = getattr(Age,minimum_age_name,Age.BABY)

        try:
            title_key = int(title_key,0)
            text_key = int(text_key,0)
        except ValueError:
            return

        sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
        if sim_info is None:
            debug_log("[AutoDynastyMod] No SimInfo found.", _connection)
            return False

        sim = sim_info.get_sim_instance()
    
        if not sim:
            return

        if (sa_id is not None and parent_sa_id is not None):

            def on_setting_change(dialog_instance):
                if not dialog_instance.accepted:
                    push_sa(sim,parent_sa_id)
                    return

                result_tag = dialog_instance.get_single_result_tag()
                debug_log(f"PICKER RESULT: {result_tag}")

                new_setting = result_tag
                        
                if result_tag == "goback":
                    push_sa(sim,parent_sa_id)
                    return

                if new_setting is not None:
                    debug_log(f"CHANGING SETTING")
                    setattr(SETTINGS,setting_name,int(new_setting))
                    SETTINGS.save()
                push_sa(sim,sa_id)

            AGE_STBL_MAP = {Age.BABY: 0x71AA5750, Age.INFANT: 0xADDA7C5E, Age.TODDLER: 0xC131542D, Age.CHILD: 0x2135D048, Age.TEEN: 0x9F66F27C, Age.YOUNGADULT: 0xD2DC11B3, Age.ADULT: 0xF54C0CD8, Age.ELDER: 0x0C48C339}

            rows=[]

            for age_enum in Age:
                if age_enum.sequential_value >= minimum_age.sequential_value:
                    rows.append(
                        {
                            "name_key": AGE_STBL_MAP.get(age_enum,0x71AA5750),
                            "tag": age_enum,
                            "is_enable": True,
                            "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == age_enum else UNSELECTED_ICON
                        }
                    )

            rows.append(
                {
                    "name_key": 0xDDC3EC7E, # Go back
                    "tag": "goback",
                    "is_enable": True,
                    "icon": GO_BACK_ICON
                }
            )

            debug_log(rows)
            
            show_item_setting_picker(sim_info,rows,on_setting_change,title_key,text_key)
    except:
        debug_log("EXCEPTION in uwaepo.dynasty_open_settings_singleage_minage_picker command:\n" + traceback.format_exc())


@sims4.commands.Command(
    'uwaepo.dynastymod_open_settings_nobleinherit_careerreqs_picker',
    command_type=sims4.commands.CommandType.Live
)
def dynasty_open_settings_nobleinherit_careerreqs_picker(setting_name: str = "", sa_key: str = "", parent_sa_key: str = "", title_key: str = "", text_key: str = "", opt_sim: OptionalSimInfoParam = None, _connection=None):
    debug_log("COMMMAND: uwaepo.dynasty_open_settings_nobleinherit_careerreqs_picker fired")
    try:
        sa_id = MOD_SA_IDS.get(sa_key)
        parent_sa_id = MOD_SA_IDS.get(parent_sa_key)

        try:
            title_key = int(title_key,0)
            text_key = int(text_key,0)
        except ValueError:
            return

        sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
        if sim_info is None:
            debug_log("[AutoDynastyMod] No SimInfo found.", _connection)
            return False

        sim = sim_info.get_sim_instance()
    
        if not sim:
            return

        if (sa_id is not None and parent_sa_id is not None):

            def on_setting_change(dialog_instance):
                if not dialog_instance.accepted:
                    push_sa(sim,parent_sa_id)
                    return

                result_tag = dialog_instance.get_single_result_tag()
                debug_log(f"PICKER RESULT: {result_tag}")

                new_setting = result_tag
                        
                if result_tag == "goback":
                    push_sa(sim,parent_sa_id)
                    return

                if new_setting is not None:
                    debug_log(f"CHANGING SETTING")
                    setattr(SETTINGS,setting_name,new_setting)
                    SETTINGS.save()
                push_sa(sim,sa_id)

            rows=[
                {
                    "name_key": 0xF2611A8D, # Unemployed Sims Only
                    "tag": "unemployedonly",
                    "is_enable": True,
                    "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == "unemployedonly" else UNSELECTED_ICON
                },
                {
                    "name_key": 0x0339D508, # Prioritise Unemployed Sims
                    "tag": "priotisedunemployed",
                    "is_enable": True,
                    "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == "priotisedunemployed" else UNSELECTED_ICON
                },
                {
                    "name_key": 0x10932571, # No Career Prioritisation
                    "tag": "all",
                    "is_enable": True,
                    "icon": SELECTED_ICON if getattr(SETTINGS,setting_name,None) == "all" else UNSELECTED_ICON
                },
                {
                    "name_key": 0xDDC3EC7E, # Go back
                    "tag": "goback",
                    "is_enable": True,
                    "icon": GO_BACK_ICON
                }
            ]
            
            show_item_setting_picker(sim_info,rows,on_setting_change,title_key,text_key)
    except:
        debug_log("EXCEPTION in uwaepo.dynasty_open_settings_nobleinherit_careerreqs_picker command:\n" + traceback.format_exc())


@sims4.commands.Command(
    'uwaepo.dynastymod_open_family_relation_picker',
    command_type=sims4.commands.CommandType.Live
)
def dynasty_open_settings_familyrelation_picker(setting_name: str = "", sa_key: str = "", parent_sa_key: str = "", raw_relation_name_list: str = "", title_key: str = "", text_key: str = "", opt_sim: OptionalSimInfoParam = None, _connection=None):
    debug_log("COMMMAND: uwaepo.dynasty_open_settings_familyrelation_picker fired")
    try:
        sa_id = MOD_SA_IDS.get(sa_key)
        parent_sa_id = MOD_SA_IDS.get(parent_sa_key)

        try:
            title_key = int(title_key,0)
            text_key = int(text_key,0)
        except ValueError:
            return

        sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
        if sim_info is None:
            debug_log("[AutoDynastyMod] No SimInfo found.", _connection)
            return False

        sim = sim_info.get_sim_instance()
    
        if not sim:
            return

        if (sa_id is not None and parent_sa_id is not None):

            def on_setting_change(dialog_instance):
                if not dialog_instance.accepted:
                    push_sa(sim,parent_sa_id)
                    return

                result_tag = dialog_instance.get_single_result_tag()

                if result_tag == "goback":
                    push_sa(sim,parent_sa_id)
                    return
                
                debug_log(f"PICKER RESULT: {result_tag}")

                new_setting = getattr(SETTINGS,setting_name,[])
                
                debug_log(f"BEFORE: {new_setting}")
                
                tag = int(result_tag)

                if tag in new_setting:
                    new_setting.remove(tag)
                else:
                    new_setting.append(tag)

                debug_log(f"AFTER: {new_setting}")

                if new_setting is not None:
                    debug_log(f"CHANGING SETTING")
                    setattr(SETTINGS,setting_name,new_setting)
                    SETTINGS.save()
                
                push_sa(sim,sa_id)

            RELATION_STBL_MAP = {RelationshipType.DESCENDANT: 0xC8ED4F64, RelationshipType.SPOUSE: 0xDD563146, RelationshipType.SIBLING: 0xB885C6ED, RelationshipType.HALF_SIBLING: 0xCA8B41D4, RelationshipType.PARENT: 0xB6A4ECC7, RelationshipType.GRANDPARENT: 0x7F9B4DB9, RelationshipType.GRANDCHILD: 0xB825263B, RelationshipType.SIBLINGS_CHILD: 0xCECB208A, RelationshipType.PARENTS_SIBLING: 0x240169FE}

            relation_name_list = raw_relation_name_list.split(",")

            rows=[]

            for relation_name in relation_name_list:
                rel_type = getattr(RelationshipType,relation_name.upper(),None)
                if rel_type is not None:
                    rows.append(
                        {
                            "name_key": RELATION_STBL_MAP.get(rel_type,0xC8ED4F64),
                            "tag": int(rel_type),
                            "is_enable": True,
                            "icon": SELECTED_ICON if int(rel_type) in getattr(SETTINGS,setting_name,None) else UNSELECTED_ICON
                        }
                    )

            rows.append(
                {
                    "name_key": 0xDDC3EC7E, # Go back
                    "tag": "goback",
                    "is_enable": True,
                    "icon": GO_BACK_ICON
                }
            )

            show_item_setting_picker(sim_info,rows,on_setting_change,title_key,text_key)
    except:
        debug_log("EXCEPTION in uwaepo.dynasty_open_settings_familyrelation_picker command:\n" + traceback.format_exc())


@sims4.commands.Command(
    'uwaepo.dynastymod_dynasty_role_picker',
    command_type=sims4.commands.CommandType.Live
)
def dynasty_open_settings_dynastyrole_picker(setting_name: str = "", sa_key: str = "", parent_sa_key: str = "", raw_role_name_list: str = "", title_key: str = "", text_key: str = "", opt_sim: OptionalSimInfoParam = None, _connection=None):
    debug_log("COMMMAND: uwaepo.dynasty_open_settings_familyrelation_picker fired")
    try:
        sa_id = MOD_SA_IDS.get(sa_key)
        parent_sa_id = MOD_SA_IDS.get(parent_sa_key)

        try:
            title_key = int(title_key,0)
            text_key = int(text_key,0)
        except ValueError:
            return

        sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
        if sim_info is None:
            debug_log("[AutoDynastyMod] No SimInfo found.", _connection)
            return False

        sim = sim_info.get_sim_instance()
    
        if not sim:
            return

        if (sa_id is not None and parent_sa_id is not None):

            def on_setting_change(dialog_instance):
                if not dialog_instance.accepted:
                    push_sa(sim,parent_sa_id)
                    return

                result_tag = dialog_instance.get_single_result_tag()

                if result_tag == "goback":
                    push_sa(sim,parent_sa_id)
                    return
                
                debug_log(f"PICKER RESULT: {result_tag}")

                new_setting = getattr(SETTINGS,setting_name,[])

                if result_tag in new_setting:
                    new_setting.remove(result_tag)
                else:
                    new_setting.append(result_tag)

                if new_setting is not None:
                    debug_log(f"CHANGING SETTING")
                    setattr(SETTINGS,setting_name,new_setting)
                    SETTINGS.save()
                
                push_sa(sim,sa_id)

            ROLE_STBL_MAP = {"head": 0x1DF47235, "heir": 0xA7CB7D0D, "member": 0x91589649, "outcast": 0xA9F83AAA}

            role_name_list = raw_role_name_list.split(",")

            rows=[]

            for role_name in role_name_list:
                if role_name is not None:
                    rows.append(
                        {
                            "name_key": ROLE_STBL_MAP.get(role_name,0x1DF47235),
                            "tag": role_name,
                            "is_enable": True,
                            "icon": SELECTED_ICON if role_name in getattr(SETTINGS,setting_name,None) else UNSELECTED_ICON
                        }
                    )

            rows.append(
                {
                    "name_key": 0xDDC3EC7E, # Go back
                    "tag": "goback",
                    "is_enable": True,
                    "icon": GO_BACK_ICON
                }
            )

            show_item_setting_picker(sim_info,rows,on_setting_change,title_key,text_key)
    except:
        debug_log("EXCEPTION in uwaepo.dynasty_open_settings_familyrelation_picker command:\n" + traceback.format_exc())
