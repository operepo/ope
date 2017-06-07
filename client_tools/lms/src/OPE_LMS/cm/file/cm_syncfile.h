#ifndef CM_SYNCFILE_H
#define CM_SYNCFILE_H

#include <QObject>
#include <QDateTime>
#include <QHash>
#include <QUuid>

#include "cm_syncfileversion.h"


class CM_SYNCFILE : QObject
{
    Q_OBJECT
public:
    CM_SYNCFILE();


    // Save the file information to the local store
    bool SaveFileInfoLocal();

    // Sync the file with the alternate locations
    bool SyncFile();


    /// STATIC METHODS
    ///

    static CM_SYNCFILE* LoadLocalFileByMD5(QString hash);
    static CM_SYNCFILE* LoadLocalFileBySHA1(QString hash);
    static CM_SYNCFILE* LoadLocalFileByGUID(QUuid uid);
    static CM_SYNCFILE* LoadLocalFileByGUID(QString uid);
    static CM_SYNCFILE* LoadLocalFileByName(QString file_name);


private:




};

#endif // CM_SYNCFILE_H
