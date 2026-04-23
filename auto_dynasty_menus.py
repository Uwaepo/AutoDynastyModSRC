import services

from interactions.context import InteractionContext
from interactions.priority import Priority

import sims4.resources

from .auto_dynasty_settings import SETTINGS
from .auto_dynasty_tuning import MOD_SA_IDS

from .ui.auto_dynasty_uidialogs import show_text_input_dialog, show_item_picker_dialog

from .utils.debug_logger import debug_log

GO_BACK_ICON = sims4.resources.get_resource_key(
    0x96de44c7d16ba610,
    0x2F7D0004
)

SELECTED_ICON = sims4.resources.get_resource_key(
    0x73339FFB0D6FFBB9,
    0x2F7D0004
)

UNSELECTED_ICON = sims4.resources.get_resource_key(
    0xCD4A2FF977E0148C,
    0x2F7D0004
)

def push_sa(sim,sa_id):
    affordance_manager = services.affordance_manager()

    interaction_tuning = affordance_manager.get(
        sims4.resources.get_resource_key(sa_id, sims4.resources.Types.INTERACTION)
    )

    if interaction_tuning is None:
        debug_log(f"WARNING: SA for interaction {sa_id} not found!")
        return

    context = InteractionContext(sim, InteractionContext.SOURCE_SCRIPT, Priority.High)
    sim.push_super_affordance(interaction_tuning, sim, context)


def show_main_settings_picker(sim_info):

    sim = sim_info.get_sim_instance()
    
    if not sim:
        return

    def on_submit(dialog_instance):

        if not dialog_instance.accepted:
            return
            
        result_tag = dialog_instance.get_single_result_tag()

        debug_log(f"PICKER RESULT: {result_tag}")
        if result_tag == "dynastysettings":
            push_sa(sim,MOD_SA_IDS["openDynastySettings_SA"])
        elif result_tag == "noblesettings":
            push_sa(sim,MOD_SA_IDS["openNobleSettings_SA"])
        elif result_tag == "resettodefault":
            SETTINGS.reset_to_defaults()

    show_item_picker_dialog(
        sim_info=sim_info,
        title_key=0xE5278BF0, # Global Mod Settings
        text_key=0x7FC6DEAB, # All settings relating to the Auto Dynasty Inheritance mod.
        rows=[
            {
                "name_key": 0xCD7923BC, # Dynasty Settings
                "row_description_key": 0xE4E2BFD4, # Settings related to automatic dynasty changes.
                "tag": "dynastysettings",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0xaf80b7c956d31a96,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0x78FB7644, # Noble Inheritance Settings
                "row_description_key": 0xEFCCDCE7, # Settings related to automatic noble title inheritance.
                "tag": "noblesettings",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0xcbfe10f0e82af944,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0x3D96688F, # Reset Settings to Default
                "row_description_key": 0x47F472F8, # Reset all settings to their default values.
                "tag": "resettodefault",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x17A3A1CF7D7514FD,
                    0x2F7D0004
                )
            }
        ],
        on_submit=on_submit
    )

def show_number_setting_picker(sim_info,setting_name,parent_sa_id,lower_bound,upper_bound,title_key,text_key,field_title_key):

    sim = sim_info.get_sim_instance()
    
    if not sim:
        return
    
    setting_value = getattr(SETTINGS,setting_name,None)

    def on_setting_change(dialog_instance,raw_value):

        if not dialog_instance.accepted:
            push_sa(sim,parent_sa_id)
            return

        debug_log(f"NUMBER PICKER RESULT: {raw_value}")

        new_setting = None
                
        try:
            new_setting = int(raw_value)
            debug_log(f"VALUE ACCEPTED: {new_setting}.")
        except ValueError:
            debug_log(f"VALUE REJECTED: {raw_value} is not an int format.")
            push_sa(sim,parent_sa_id)
            return

        if not (lower_bound <= new_setting <= upper_bound):
            debug_log(f"VALUE REJECTED: {new_setting} is not within {lower_bound}-{upper_bound}.")
            push_sa(sim,parent_sa_id)
            return

        if new_setting is not None:
            debug_log(f"CHANGING SETTING")
            setattr(SETTINGS,setting_name,new_setting)
            SETTINGS.save()

        push_sa(sim,parent_sa_id)

    show_text_input_dialog(
        sim_info=sim_info,
        title_key=title_key,
        text_key=text_key,
        field_title_key=field_title_key,
        on_submit=on_setting_change,
        initial_value=str(setting_value)
    )

def show_enable_disable_picker(sim_info, title_key, text_key, on_submit, is_enabled=False):

    if on_submit is None:
        return

    show_item_picker_dialog(
        sim_info=sim_info,
        title_key=title_key,
        text_key=text_key,
        rows=[
            {
                "name_key": 0x191FB38E, # Enable
                "row_description_key": 0x8694FC5B, # This setting will be enabled.
                "tag": "true",
                "is_enable": True,
                "icon": SELECTED_ICON if is_enabled == True else UNSELECTED_ICON
            },
            {
                "name_key": 0x74E14A55, # Disable
                "row_description_key": 0x9E8F57EC, # This setting will be disabled.
                "tag": "false",
                "is_enable": True,
                "icon": SELECTED_ICON if is_enabled == False else UNSELECTED_ICON
            },
            {
                "name_key": 0xDDC3EC7E, # Go back
                "tag": "goback",
                "is_enable": True,
                "icon": GO_BACK_ICON
            }
        ],
        on_submit=on_submit
    )

def show_enable_disable_setting_picker(sim_info,setting_name,sa_id,parent_sa_id,title_key,text_key):

    sim = sim_info.get_sim_instance()
    
    if not sim:
        return
    
    setting_value = getattr(SETTINGS,setting_name,None)

    def on_setting_change(dialog_instance):

        if not dialog_instance.accepted:
            push_sa(sim,parent_sa_id)
            return

        result_tag = dialog_instance.get_single_result_tag()
        debug_log(f"PICKER RESULT: {result_tag}")

        new_setting = None
                
        if result_tag == "true":
            new_setting = True
        elif result_tag == "false":
            new_setting = False
        elif result_tag == "goback":
            push_sa(sim,parent_sa_id)
            return

        if new_setting is not None:
            debug_log(f"CHANGING SETTING")
            setattr(SETTINGS,setting_name,new_setting)
            SETTINGS.save()
        push_sa(sim,sa_id)

    show_enable_disable_picker(
        sim_info=sim_info,
        title_key=title_key,
        text_key=text_key,
        on_submit=on_setting_change,
        is_enabled=bool(setting_value)
    )


def show_item_setting_picker(sim_info,rows,on_submit,title_key,text_key):

    sim = sim_info.get_sim_instance()
    
    if not sim:
        return

    show_item_picker_dialog(
        sim_info=sim_info,
        title_key=title_key,
        text_key=text_key,
        rows=rows,
        on_submit=on_submit
    )


def show_dynasty_settings_picker(sim_info):

    sim = sim_info.get_sim_instance()
    
    if not sim:
        return

    def on_submit(dialog_instance):

        if not dialog_instance.accepted:
            push_sa(sim,MOD_SA_IDS["openGlobalSettings_SA"])
            return

        result_tag = dialog_instance.get_single_result_tag()
        services.ui_dialog_service().dialog_cancel(dialog_instance.dialog_id)
        debug_log(f"PICKER RESULT: {result_tag}")

        if result_tag == "masterdynastysetting":
            push_sa(sim,MOD_SA_IDS["openGlobalDynastyModEnabler_SA"])
        elif result_tag == "childsettings":
            push_sa(sim,MOD_SA_IDS["openDynastyChildrenSub_SA"])
        elif result_tag == "marriagesettings":
            push_sa(sim,MOD_SA_IDS["openDynastyMarriageSub_SA"])
        elif result_tag == "heirsettings":
            push_sa(sim,MOD_SA_IDS["openDynastyHeirSub_SA"])
        elif result_tag == "outcastsettings":
            push_sa(sim,MOD_SA_IDS["openDynastyBlackSheepSub_SA"])
        elif result_tag == "relationssettings":
            push_sa(sim,MOD_SA_IDS["openDynastyRelationsSub_SA"])
        elif result_tag == "goback":
            push_sa(sim,MOD_SA_IDS["openGlobalSettings_SA"])

    show_item_picker_dialog(
        sim_info=sim_info,
        title_key=0xCD7923BC, # Dynasty Settings
        text_key=0xE4E2BFD4, # Settings related to automatic dynasty changes.
        rows=[
            {
                "name_key": 0x4C09A7FD, # [MASTER] Enable/Disable Automatic Dynasty Changes
                "row_description_key": 0xC373F173, # Disabling this setting will stop the mod from adding new members, changing dynasty roles and creating alliances/rivalries automatically.
                "tag": "masterdynastysetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x18ec456d71d7a22e,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xFEF90C8A, # Child/Adoption Settings
                "row_description_key": 0x685E782D, # Settings related to dymasty births and adoption..
                "tag": "childsettings",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0xff12fd8eb30fb93b,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xBDB73C98, # Marriage Settings
                "row_description_key": 0xB58B7541, # Settings related to dynasty marriages.
                "tag": "marriagesettings",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x13fab148329e8988,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xFEDF1D43, # Dynasty Heir Settings
                "row_description_key": 0xA94B677A, # Settings related to dynasty heir selection.
                "tag": "heirsettings",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0xf95619610b6d7ec6,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0x22BE0DC5, # Dynasty Outcast Settings
                "row_description_key": 0x99488EC3, # Settings related to dynasty outcast selection.
                "tag": "outcastsettings",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x94be6e418b9790e8,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0x5379C75B, # Dynasty Relations (Alliances/Rivalries) Settings
                "row_description_key": 0xD5FDB781, # Settings related to dynasty allies and rivals selection.
                "tag": "relationssettings",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x2232ACF0EE575326,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xDDC3EC7E, # Go back
                "tag": "goback",
                "is_enable": True,
                "icon": GO_BACK_ICON
            }
        ],
        on_submit=on_submit
    )

def show_dynastychild_settings_picker(sim_info):

    sim = sim_info.get_sim_instance()
    
    if not sim:
        return

    def on_submit(dialog_instance):

        if not dialog_instance.accepted:
            push_sa(sim,MOD_SA_IDS["openDynastySettings_SA"])
            return

        result_tag = dialog_instance.get_single_result_tag()

        debug_log(f"PICKER RESULT: {result_tag}")
        if result_tag == "masterchildsetting":
            push_sa(sim,MOD_SA_IDS["openGlobalDynastyChildrenEnabler_SA"])
        elif result_tag == "childrentoaddsetting":
            push_sa(sim,MOD_SA_IDS["openAllowWhichChildrenPicker_SA"])
        elif result_tag == "goback":
            push_sa(sim,MOD_SA_IDS["openDynastySettings_SA"])

    show_item_picker_dialog(
        sim_info=sim_info,
        title_key=0xFEF90C8A, # Child/Adoption Settings
        text_key=0x685E782D, # Settings related to dymasty births and adoption.
        rows=[
            {
                "name_key": 0x4AC312D7, # [MASTER] Enable/Disable Children Joining Dynasties
                "row_description_key": 0xF7D01237, # Disabling this setting will stop the mod from adding new children to dynasties automatically.
                "tag": "masterchildsetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0xff12fd8eb30fb93b,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0x2241BFB2, # Required Parent Dynasty Role
                "row_description_key": 0xB30B2D0A, # The required role (Head/Heir/Member) a parent must be for their child to be added to their dynasty.
                "tag": "childrentoaddsetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0xA8AE08E5B77C91CA,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xDDC3EC7E, # Go back
                "tag": "goback",
                "is_enable": True,
                "icon": GO_BACK_ICON
            }
        ],
        on_submit=on_submit
    )

def show_dynastymarriage_settings_picker(sim_info):

    sim = sim_info.get_sim_instance()
    
    if not sim:
        return

    def on_submit(dialog_instance):

        if not dialog_instance.accepted:
            push_sa(sim,MOD_SA_IDS["openDynastySettings_SA"])
            return

        result_tag = dialog_instance.get_single_result_tag()

        debug_log(f"PICKER RESULT: {result_tag}")
        if result_tag == "mastermarriagesetting":
            push_sa(sim,MOD_SA_IDS["openGlobalDynastyMarriageEnabler_SA"])
        elif result_tag == "spousetoaddsetting":
            push_sa(sim,MOD_SA_IDS["openAllowWhichSpousePicker_SA"])
        elif result_tag == "goback":
            push_sa(sim,MOD_SA_IDS["openDynastySettings_SA"])

    show_item_picker_dialog(
        sim_info=sim_info,
        title_key=0xBDB73C98, # Marriage Settingss
        text_key=0xB58B7541, # Settings related to dynasty marriages.
        rows=[
            {
                "name_key": 0x96BB208A, # [MASTER] Enable/Disable Spouses Joining Dynasties
                "row_description_key": 0x9ADCA4D2, # Disabling this setting will stop the mod from adding new spouses to dynasties automatically.
                "tag": "mastermarriagesetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x13fab148329e8988,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0x4DBA0D50, # Required Spouse Dynasty Role
                "row_description_key": 0x4FC26CD1, # The required role (Head/Heir/Member) a sims spouse must be to join their dynasty.
                "tag": "spousetoaddsetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0xA8AE08E5B77C91CA,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xDDC3EC7E, # Go back
                "tag": "goback",
                "is_enable": True,
                "icon": GO_BACK_ICON
            }
        ],
        on_submit=on_submit
    )


def show_dynastyheir_settings_picker(sim_info):

    sim = sim_info.get_sim_instance()
    
    if not sim:
        return

    def on_submit(dialog_instance):

        if not dialog_instance.accepted:
            push_sa(sim,MOD_SA_IDS["openDynastySettings_SA"])
            return
        
        result_tag = dialog_instance.get_single_result_tag()

        debug_log(f"PICKER RESULT: {result_tag}")
        if result_tag == "masterheirsetting":
            push_sa(sim,MOD_SA_IDS["openGlobalDynastyHeirEnabler_SA"])
        elif result_tag == "heirthresholdsetting":
            push_sa(sim,MOD_SA_IDS["openDynastyHeirRelThresholdPicker_SA"])
        elif result_tag == "goback":
            push_sa(sim,MOD_SA_IDS["openDynastySettings_SA"])

    show_item_picker_dialog(
        sim_info=sim_info,
        title_key=0xFEDF1D43, # Dynasty Heir Settings
        text_key=0xA94B677A, # Settings related to dynasty heir selection.
        rows=[
            {
                "name_key": 0x25C13928, # [MASTER] Enable/Disable Automatic Heir Selection
                "row_description_key": 0x3B77FBE4, # Disabling this setting will stop the mod from selecting new/removing existing heirs automatically.
                "tag": "masterheirsetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0xf95619610b6d7ec6,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xFCB161D5, # Minimum Head-Heir Relationship Threshold
                "row_description_key": 0x6F02B3B5, # The minimum friendly relationship a member must have with the head sim to qualify as an heir.
                "tag": "heirthresholdsetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0xF7B24997BB018051,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xDDC3EC7E, # Go back
                "tag": "goback",
                "is_enable": True,
                "icon": GO_BACK_ICON
            },
        ],
        on_submit=on_submit
    )


def show_dynastyblacksheep_settings_picker(sim_info):

    sim = sim_info.get_sim_instance()
    
    if not sim:
        return

    def on_submit(dialog_instance):

        if not dialog_instance.accepted:
            push_sa(sim,MOD_SA_IDS["openDynastySettings_SA"])
            return#
        
        result_tag = dialog_instance.get_single_result_tag()

        debug_log(f"PICKER RESULT: {result_tag}")
        if result_tag == "masteroutcastsetting":
            push_sa(sim,MOD_SA_IDS["openGlobalDynastyOutcastEnabler_SA"])
        elif result_tag == "addoutcastthresholdsetting":
            push_sa(sim,MOD_SA_IDS["openDynastyDelcareOutcastRelThresholdPicker_SA"])
        elif result_tag == "removeoutcastthresholdsetting":
            push_sa(sim,MOD_SA_IDS["openDynastyRevokeOutcastRelThresholdPicker_SA"])
        elif result_tag == "goback":
            push_sa(sim,MOD_SA_IDS["openDynastySettings_SA"])

    show_item_picker_dialog(
        sim_info=sim_info,
        title_key=0x22BE0DC5, # Dynasty Outcast Settings
        text_key=0x99488EC3, # Settings related to dynasty outcast selection.
        rows=[
            {
                "name_key": 0xCD2F0DCB, # [MASTER] Enable/Disable Automatic Outcast Selection
                "row_description_key": 0x32E9D77F, # Disabling this setting will stop the mod from selecting/removing outcasts automatically.
                "tag": "masteroutcastsetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x94be6e418b9790e8,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0x1CD09410, # Declare Outcast Status Relationship Threshold
                "row_description_key": 0xC8B2DAC8, # The friendly relationship an outcast must have with the head to be declared an outcast. (-100 to 100, default: -60)
                "tag": "addoutcastthresholdsetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x92FB0F1404F8DE36,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0x9C021205, # Revoke Outcast Status Relationship Threshold
                "row_description_key": 0x58CD5EE7, # The friendly relationship an outcast must have with the head to stop being an outcast. (-100 to 100, default: 0)
                "tag": "removeoutcastthresholdsetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x88B85C6C87EA7CD0,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xDDC3EC7E, # Go back
                "tag": "goback",
                "is_enable": True,
                "icon": GO_BACK_ICON
            },
        ],
        on_submit=on_submit
    )

def show_noble_settings_picker(sim_info):

    sim = sim_info.get_sim_instance()
    
    if not sim:
        return

    def on_submit(dialog_instance):

        if not dialog_instance.accepted:
            push_sa(sim,MOD_SA_IDS["openGlobalSettings_SA"])
            return

        result_tag = dialog_instance.get_single_result_tag()
        services.ui_dialog_service().dialog_cancel(dialog_instance.dialog_id)
        debug_log(f"PICKER RESULT: {result_tag}")

        if result_tag == "masternoblesetting":
            push_sa(sim,MOD_SA_IDS["openGlobalNobleInheritanceEnabler_SA"])
        elif result_tag == "noblethresholdsetting":
            push_sa(sim,MOD_SA_IDS["openNobleInheritanceRelThresholdPicker_SA"])
        elif result_tag == "goback":
            push_sa(sim,MOD_SA_IDS["openGlobalSettings_SA"])

    show_item_picker_dialog(
        sim_info=sim_info,
        title_key=0x78FB7644, # Noble Inheritance Settings
        text_key=0xEFCCDCE7, # Settings related to automatic noble title inheritance.
        rows=[
            {
                "name_key": 0x60648602, # [MASTER] Enable/Disable Automatic Noble Title Inheritance
                "row_description_key": 0x1D253C4A, # Disabling this setting will stop the mod from setting inherited noble titles automatically.
                "tag": "masternoblesetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0xcbfe10f0e82af944,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xF245383B, # Noble Title Inheritance Relationship Threshold
                "row_description_key": 0xE69BF835, # The minimum friendly relationship a member must have with the a noble to qualify to inherit their title. (-100 to 100, default: 0)
                "tag": "noblethresholdsetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0xA2B935892F831E86,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xDDC3EC7E, # Go back
                "tag": "goback",
                "is_enable": True,
                "icon": GO_BACK_ICON
            }
        ],
        on_submit=on_submit
    )


def show_dynastyrelations_settings_picker(sim_info):

    sim = sim_info.get_sim_instance()
    
    if not sim:
        return

    def on_submit(dialog_instance):

        if not dialog_instance.accepted:
            push_sa(sim,MOD_SA_IDS["openDynastySettings_SA"])
            return#
        
        result_tag = dialog_instance.get_single_result_tag()

        debug_log(f"PICKER RESULT: {result_tag}")
        if result_tag == "masterrelationssetting":
            push_sa(sim,MOD_SA_IDS["openGlobalDynastyRelationsEnabler_SA"])
        elif result_tag == "alliancesettings":
            push_sa(sim,MOD_SA_IDS["openDynastyAlliancesSub_SA"])
        elif result_tag == "rivalrysettings":
            push_sa(sim,MOD_SA_IDS["openDynastyRivalriesSub_SA"])
        elif result_tag == "goback":
            push_sa(sim,MOD_SA_IDS["openDynastySettings_SA"])

    show_item_picker_dialog(
        sim_info=sim_info,
        title_key=0x5379C75B, # Dynasty Relations (Alliances/Rivalries) Settings
        text_key=0xD5FDB781, # Settings related to dynasty allies and rivals selection.
        rows=[
            {
                "name_key": 0x4AC226C0, # [MASTER] Enable/Disable Automatic Dynasty Relations
                "row_description_key": 0x77036E5D, # Disabling this setting will stop the mod from starting and ending alliances and rivalries automatically.
                "tag": "masterrelationssetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x2232ACF0EE575326,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0x8889CDE8, # Alliance Settings
                "row_description_key": 0x5677091C, # Settings related to automatic ally selection.
                "tag": "alliancesettings",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x5BB5F489525055D7,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0x6B6FAB76, # Rivalry Settings
                "row_description_key": 0x104B103B, # Settings related to automatic rival selection.
                "tag": "rivalrysettings",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0xF9D3CA2C7D757014,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xDDC3EC7E, # Go back
                "tag": "goback",
                "is_enable": True,
                "icon": GO_BACK_ICON
            },
        ],
        on_submit=on_submit
    )


def show_dynastyrelations_alliances_picker(sim_info):

    sim = sim_info.get_sim_instance()
    
    if not sim:
        return

    def on_submit(dialog_instance):

        if not dialog_instance.accepted:
            push_sa(sim,MOD_SA_IDS["openDynastyRelationsSub_SA"])
            return#
        
        result_tag = dialog_instance.get_single_result_tag()

        debug_log(f"PICKER RESULT: {result_tag}")
        if result_tag == "masternewalliancesetting":
            push_sa(sim,MOD_SA_IDS["openGlobalNewAlliancesEnabler_SA"])
        elif result_tag == "masterremovealliancesetting":
            push_sa(sim,MOD_SA_IDS["openGlobalRemoveAlliancesEnabler_SA"])
        elif result_tag == "headrelnewallythresholdsetting":
            push_sa(sim,MOD_SA_IDS["openDynastyAllianceHeadRelThresholdPicker_SA"])
        elif result_tag == "avgrelnewallythresholdsetting":
            push_sa(sim,MOD_SA_IDS["openDynastyAllianceAvgRelThresholdPicker_SA"])
        elif result_tag == "levelgapnewallysetting":
            push_sa(sim,MOD_SA_IDS["openDynastyAlliancePrestigeGapPicker_SA"])
        elif result_tag == "headrelremoveallythresholdsetting":
            push_sa(sim,MOD_SA_IDS["openDynastyRemoveAllianceHeadRelThresholdPicker_SA"])
        elif result_tag == "avgrelremoveallythresholdsetting":
            push_sa(sim,MOD_SA_IDS["openDynastyRemoveAllianceAvgRelThresholdPicker_SA"])
        elif result_tag == "goback":
            push_sa(sim,MOD_SA_IDS["openDynastyRelationsSub_SA"])

    show_item_picker_dialog(
        sim_info=sim_info,
        title_key=0x8889CDE8, # Alliance Settings
        text_key=0x5677091C, # Settings related to automatic ally selection.
        rows=[
            {
                "name_key": 0x22740FC4, # [MASTER] Enable/Disable Automatic New Alliances
                "row_description_key": 0xBF29F4A1, # Disabling this setting will stop the mod from starting new alliances automatically.
                "tag": "masternewalliancesetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x5BB5F489525055D7,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xBE9A493D, # [MASTER] Enable/Disable Automatic Remove Alliances
                "row_description_key": 0x425BAE31, # Disabling this setting will stop the mod from ending existing alliances automatically.
                "tag": "masterremovealliancesetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x9DCA51D21105BB44,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xF7E5172E, # Minimum Head-Head Relationship Threshold
                "row_description_key": 0xD73E3265, # The minimum friendly relationship two head sims must have to potentially start an alliance.
                "tag": "headrelnewallythresholdsetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x54907B7F1AF4E404,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0x7F756F5A, # Minimum Average Head-Members Relationship Threshold
                "row_description_key": 0xFFCA2622, # The average friendly relationship a head sim must have with all sims of another dynasty to potentially start an alliance.
                "tag": "avgrelnewallythresholdsetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0xA2B935892F831E86,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xC0F5CE91, # Prestige Level Gap
                "row_description_key": 0xF3DDAF2F, # The maximum gap in prestige levels two dynasties can be to consider a new alliance.
                "tag": "levelgapnewallysetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x51B9F5A1618C2FC7,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0x9846AE86, # Minimum Head-Head Relationship Threshold (Remove Alliance)
                "row_description_key": 0x82A7DE10, # The friendly relationship two head sims must have to end an existing alliance.
                "tag": "headrelremoveallythresholdsetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x46440178CBE57DBF,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xA10159F9, # Minimum Average Head-Members Relationship Threshold (Remove Alliance)
                "row_description_key": 0x03779918, # The average friendly relationship a head sim must have with all sims of another dynasty to end an alliance.
                "tag": "avgrelremoveallythresholdsetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0xBC75B8F98F2DBDD4,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xDDC3EC7E, # Go back
                "tag": "goback",
                "is_enable": True,
                "icon": GO_BACK_ICON
            },
        ],
        on_submit=on_submit
    )


def show_dynastyrelations_rivalries_picker(sim_info):

    sim = sim_info.get_sim_instance()
    
    if not sim:
        return

    def on_submit(dialog_instance):

        if not dialog_instance.accepted:
            push_sa(sim,MOD_SA_IDS["openDynastyRelationsSub_SA"])
            return#
        
        result_tag = dialog_instance.get_single_result_tag()

        debug_log(f"PICKER RESULT: {result_tag}")
        if result_tag == "masternewrivalrysetting":
            push_sa(sim,MOD_SA_IDS["openGlobalNewRivalriesEnabler_SA"])
        elif result_tag == "masterremoverivalrysetting":
            push_sa(sim,MOD_SA_IDS["openGlobalRemoveRivalriesEnabler_SA"])
        elif result_tag == "headrelnewrivalthresholdsetting":
            push_sa(sim,MOD_SA_IDS["openDynastyRivalryHeadRelThresholdPicker_SA"])
        elif result_tag == "avgrelnewrivalthresholdsetting":
            push_sa(sim,MOD_SA_IDS["openDynastyRivalryAvgRelThresholdPicker_SA"])
        elif result_tag == "headrelremoverivalthresholdsetting":
            push_sa(sim,MOD_SA_IDS["openDynastyRemoveRivalryHeadRelThresholdPicker_SA"])
        elif result_tag == "goback":
            push_sa(sim,MOD_SA_IDS["openDynastyRelationsSub_SA"])

    show_item_picker_dialog(
        sim_info=sim_info,
        title_key=0x6B6FAB76, # Rivalry Settings
        text_key=0x104B103B, # Settings related to automatic rival selection.
        rows=[
            {
                "name_key": 0xBCFFC2AE, # [MASTER] Enable/Disable Automatic New Rivalries
                "row_description_key": 0x8AEB644F, # Disabling this setting will stop the mod from starting new rivalries automatically.
                "tag": "masternewrivalrysetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0xF9D3CA2C7D757014,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xA1EAB1E8, # [MASTER] Enable/Disable Automatic Remove Rivalries
                "row_description_key": 0x16E9E548, # Disabling this setting will stop the mod from ending existing rivalries automatically.
                "tag": "masterremoverivalrysetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x29ED7EC6BBB9429C,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0x17BBEDC4, # Minimum Head-Head Relationship Threshold (New Rivalry)
                "row_description_key": 0xADAA554E, # The friendly relationship two head sims must have to potentially start a new rivalry. (-100 to 100, default: -50)
                "tag": "headrelnewrivalthresholdsetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x857F238D00BCF205,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0x7813F296, # Minimum Average Head-Members Relationship Threshold (New Rivalry)
                "row_description_key": 0x4093951A, # The average friendly relationship a head sim must have with all sims of another dynasty to potentially start a rivalry.
                "tag": "avgrelnewrivalthresholdsetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0xFB9988AC57EDA80A,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xDDAB7576, # Minimum Head-Head Relationship Threshold (Remove Rivalry)
                "row_description_key": 0x38C7A0A0, # The friendly relationship two head sims must have to end an existing rivalry.
                "tag": "headrelremoverivalthresholdsetting",
                "is_enable": True,
                "icon": sims4.resources.get_resource_key(
                    0x29ED7EC6BBB9429C,
                    0x2F7D0004
                )
            },
            {
                "name_key": 0xDDC3EC7E, # Go back
                "tag": "goback",
                "is_enable": True,
                "icon": GO_BACK_ICON
            },
        ],
        on_submit=on_submit
    )