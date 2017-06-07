#include "cm_fileinfo.h"

CM_FileInfo::CM_FileInfo()
{    

}

QString CM_FileInfo::GetFileName()
{
    return _VALUES["file_name"];
}

bool CM_FileInfo::SetFileName(QString file_name)
{
    bool ret = true;

    _VALUES["file_name"] = file_name;

    qDebug() << "cm_fileinfo - SetFileName: " << file_name;

    return ret;
}


