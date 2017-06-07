#include "sc_modulemodel.h"

SC_ModuleModel::SC_ModuleModel(QObject *parent) :
    CM_PersistentObjectModel(parent)
{
    loadItemList();
}
