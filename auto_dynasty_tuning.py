# *Python Modules*
import traceback

# *Sims 4 Modules*
import services
import sims4.resources

from sims4.resources import Types
from sims4.tuning.instance_manager import InstanceManager

# *My Modules*
from .utils.injection import inject_to
from .utils.debug_logger import debug_log

# *Constants*
MOD_SA_IDS = {
    "openGlobalSettings_SA": 4100603253821006077,
    "openDynastySettings_SA": 2277539424149250580,
    "openNobleSettings_SA": 12996693458383374788,

    "openGlobalDynastyModEnabler_SA": 16840106932251952337,

    "openGlobalNobleInheritanceEnabler_SA": 11298748893984418377,
    "openNobleInheritanceRelThresholdPicker_SA": 15602580910547423574,

    "openDynastyChildrenSub_SA": 5268191022460015977,
    "openGlobalDynastyChildrenEnabler_SA": 1692262163354922680,
    "openAllowWhichChildrenPicker_SA": 1844658760351774399,

    "openDynastyMarriageSub_SA": 15587813555881591716,
    "openGlobalDynastyMarriageEnabler_SA": 14410644551782732203,
    "openAllowWhichSpousePicker_SA": 18319400644165084791,
    
    "openDynastyHeirSub_SA": 4095023956375673512,
    "openGlobalDynastyHeirEnabler_SA": 564242234709985375,
    "openDynastyHeirRelThresholdPicker_SA": 15835642838527574006,

    "openDynastyBlackSheepSub_SA": 8851396749071259894,
    "openGlobalDynastyOutcastEnabler_SA": 12499293592649829330,
    "openDynastyDelcareOutcastRelThresholdPicker_SA": 8940125178568154422,
    "openDynastyRevokeOutcastRelThresholdPicker_SA": 17855539998382457840,

    "openDynastyRelationsSub_SA": 937861700694428407,
    "openGlobalDynastyRelationsEnabler_SA": 12918482440665004436,

    "openDynastyAlliancesSub_SA": 4022254939209674594,
    "openGlobalNewAlliancesEnabler_SA": 7394249466769942519,
    "openGlobalRemoveAlliancesEnabler_SA": 9964585463645443267,
    "openDynastyAllianceHeadRelThresholdPicker_SA": 2921647997459461763,
    "openDynastyAllianceAvgRelThresholdPicker_SA": 9712031112468781175,
    "openDynastyAlliancePrestigeGapPicker_SA": 8571810085009604724,
    "openDynastyRemoveAllianceHeadRelThresholdPicker_SA": 3336802913025566815,
    "openDynastyRemoveAllianceAvgRelThresholdPicker_SA": 17912877431276497659,

    "openDynastyRivalriesSub_SA": 8388638178932039303,
    "openGlobalNewRivalriesEnabler_SA": 10302251031919458332,
    "openGlobalRemoveRivalriesEnabler_SA": 16290196977006660736,
    "openDynastyRivalryHeadRelThresholdPicker_SA": 14228181524848590843,
    "openDynastyRivalryAvgRelThresholdPicker_SA": 7250669180194868015,
    "openDynastyRemoveRivalryHeadRelThresholdPicker_SA": 6220072595640922719,
}

SA_IDS_TO_INJECT = (
    MOD_SA_IDS["openGlobalSettings_SA"],
)


OBJECT_SIM_ID = 14965

def add_super_affordances_to_sims(instance_manager):
    affordance_manager = services.affordance_manager()
    sa_list = []

    for sa_id in SA_IDS_TO_INJECT:
        key = sims4.resources.get_resource_key(sa_id, Types.INTERACTION)
        sa_tuning = affordance_manager.get(key)
        if sa_tuning is not None:
            sa_list.append(sa_tuning)

    sa_tuple = tuple(sa_list)

    key = sims4.resources.get_resource_key(OBJECT_SIM_ID, Types.OBJECT)
    object_sim = instance_manager._tuned_classes.get(key)

    if object_sim is not None:
        object_sim._super_affordances += sa_tuple


@inject_to(InstanceManager, 'load_data_into_class_instances')
def instance_manager_load_data_into_class_instances(original, self, *args, **kwargs):
    debug_log("HOOK: InstanceManager.load_data_into_class_instances fired")
    result = original(self, *args, **kwargs)

    try:
        if self.TYPE == Types.OBJECT:
            add_super_affordances_to_sims(self)
    except:
        debug_log("EXCEPTION in InstanceManager.load_data_into_class_instances hook:\n" + traceback.format_exc())
        
    return result
