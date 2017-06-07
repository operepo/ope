#include "sc_classmodel.h"

SC_ClassModel::SC_ClassModel(QObject *parent) :
    CM_PersistentObjectModel(parent)
{
    loadItemList();
}

