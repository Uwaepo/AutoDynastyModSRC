import sims4.resources

from sims4.collections import AttributeDict
from sims4.localization import LocalizationHelperTuning
from sims4.tuning.tunable import TunableTuple

from ui.ui_dialog_generic import UiDialogTextInputOkCancel, UiTextInput
from ui.ui_dialog_picker import UiItemPicker, BasePickerRow
from ui.ui_text_input import _TextInputLengthFixed

from ..utils.debug_logger import debug_log

class MinLengthData:
    def __init__(self, length, tooltip=None):
        self.length = length
        self.tooltip = tooltip

def loc_with_tokens(key, *tokens):
    if not tokens:
        return sims4.localization._create_localized_string(key)

    localized_tokens = tuple(
        LocalizationHelperTuning.get_raw_text(str(t))
        for t in tokens
    )

    return sims4.localization._create_localized_string(key, localized_tokens)

def show_notification(sim_info, title_key=None, text_key=None):
    title = lambda **_: sims4.localization._create_localized_string(title_key)
    text = lambda **_: sims4.localization._create_localized_string(text_key)

    notification = UiDialogNotification.TunableFactory().default(
        sim_info,
        title=title,
        text=text
    )

    notification.show_dialog()

def show_text_input_dialog(sim_info, title_key, text_key, field_title_key, on_submit, initial_value=""):

    length_restriction = _TextInputLengthFixed(
        min_length=MinLengthData(length=1, tooltip=None),
        max_length=10
    )
    
    text_input = UiTextInput(
        sort_order=0,
        title= lambda **_: sims4.localization._create_localized_string(field_title_key),
        initial_value= lambda **_: LocalizationHelperTuning.get_raw_text(str(initial_value)),
        default_text=None,
        length_restriction=length_restriction,
        restricted_characters=None,
        check_profanity=False,
        height=None
    )

    text_inputs_dict = AttributeDict()
    text_inputs_dict["value"] = text_input

    dialog = UiDialogTextInputOkCancel.TunableFactory().default(
        sim_info,
        title= lambda **_: sims4.localization._create_localized_string(title_key),
        text= lambda **_: sims4.localization._create_localized_string(text_key),
        text_inputs=text_inputs_dict
    )

    def _on_response(dialog_instance):
        debug_log("ON_RESPONSE FIRED")
        debug_log(f"RESPONSES DICT: {dialog_instance.text_input_responses}")

        raw_value = dialog_instance.text_input_responses.get("value", "")

        debug_log(f"VALUE PASSED: {raw_value}")

        on_submit(dialog_instance,raw_value)

    dialog.add_listener(_on_response)
    dialog.show_dialog()

def show_item_picker_dialog(sim_info, title_key, text_key, rows, on_submit):

    picker_dialog = UiItemPicker.TunableFactory().default(
        sim_info,
        title= lambda **_: sims4.localization._create_localized_string(title_key),
        text= lambda **_: sims4.localization._create_localized_string(text_key),
    )

    for row_data in rows:
        row_description = None

        if row_data.get("row_description_key") != None:
            row_description = sims4.localization._create_localized_string(row_data["row_description_key"])

        row = BasePickerRow(
            name=sims4.localization._create_localized_string(row_data["name_key"]),
            row_description=row_description,
            tag=row_data["tag"],
            is_enable=row_data["is_enable"],
            icon=row_data.get("icon") or None,
            is_selected=False
        )

        picker_dialog.add_row(row)

    def _on_response(dialog_instance):
        debug_log("ON_RESPONSE FIRED")
        
        if not dialog_instance.accepted:
            return

        debug_log(f"VALUE RESULT: {dialog_instance.get_single_result_tag()}")

        on_submit(dialog_instance)

    picker_dialog.add_listener(_on_response)
    picker_dialog.show_dialog()
