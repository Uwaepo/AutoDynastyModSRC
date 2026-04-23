# *Python Modules*
import traceback

# *Sims 4 Modules*
import sims4.commands
from server_commands.argument_helpers import OptionalSimInfoParam, get_optional_target

from .ui.auto_dynasty_uidialogs import show_text_input_dialog, show_item_picker_dialog
from .utils.debug_logger import debug_log

# *My Modules*
from .auto_dynasty_menus import push_sa, show_main_settings_picker, show_dynasty_settings_picker, show_noble_settings_picker, show_enable_disable_setting_picker, show_number_setting_picker, show_item_setting_picker, show_dynastychild_settings_picker, show_dynastymarriage_settings_picker, show_dynastyheir_settings_picker, show_dynastyblacksheep_settings_picker, show_dynastyrelations_settings_picker, show_dynastyrelations_alliances_picker, show_dynastyrelations_rivalries_picker, SELECTED_ICON, UNSELECTED_ICON, GO_BACK_ICON
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