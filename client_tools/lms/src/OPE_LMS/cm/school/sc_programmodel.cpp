#include "sc_programmodel.h"

SC_ProgramModel::SC_ProgramModel(QObject *parent): CM_PersistentObjectModel(parent)
{
    //qDebug() << "SC_ProgramModel - Constructor";
    loadItemList();
}

