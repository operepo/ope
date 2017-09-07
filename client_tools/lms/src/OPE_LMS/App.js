.pragma library

var current_course = "";


function getFieldValue(model, row, field_name) {
    var ret = undefined;
    ret = model.data(model.index(row, model.getColumnIndex(field_name)), Qt.DisplayRole);
    return ret;
}
