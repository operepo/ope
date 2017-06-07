#include "sc_lessonitemmodel.h"

SC_LessonItemModel::SC_LessonItemModel(QObject *parent) :
    CM_PersistentObjectModel(parent)
{
    loadItemList();
}
