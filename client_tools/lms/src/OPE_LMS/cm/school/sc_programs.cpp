#include "sc_programs.h"

SC_Programs::SC_Programs(QObject *parent) :CM_PersistentObject(parent)
{
    object_type = "programs";
    //qDebug() << "SC_Programs - Setting object_type";
}
