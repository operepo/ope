#ifndef CM_SYNCFILEVERSION_H
#define CM_SYNCFILEVERSION_H


#include <QObject>
#include <QDateTime>
#include <QHash>
#include <QUuid>

#include "cm_syncfilechunk.h"


class CM_SyncFileVersion : QObject
{
    Q_OBJECT
public:
    CM_SyncFileVersion();


private:
    QString _file_name;
    QString _file_path;
    QUuid _file_guid;
    QUuid _version_guid;
    QDateTime _last_synced;
    QDateTime _last_file_modification;
    long int _last_file_size;
    int _file_version;

    QString _file_state;

    QString _file_sha1_hash;
    QString _file_md5_hash;

    QHash<int, CM_SyncFileChunk> _file_chunks;
};

#endif // CM_SYNCFILEVERSION_H
