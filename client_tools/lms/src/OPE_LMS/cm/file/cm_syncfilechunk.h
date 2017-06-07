#ifndef CM_SYNCFILECHUNK_H
#define CM_SYNCFILECHUNK_H

#include <QObject>
#include <QDateTime>
#include <QHash>
#include <QUuid>



class CM_SyncFileChunk : QObject
{
    Q_OBJECT
public:
    CM_SyncFileChunk();

    // Load and return the chunk
    QByteArray *GetChunk();

    // Set the chunk for this object
    void SetChunk(QByteArray *);

    // Load the chunk from the local or remote repository
    bool LoadChunk();

    // Save the chunk to the local location
    bool SaveChunkLocal();

private:
    // A unique uuid for this chunk
    // UUID is assigned by the server and null until then
    QUuid _chunk_uuid;

    // Hash the chunk using 2 methods to ensure no collision
    QString _chunk_sha1_hash;
    QString _chunk_md5_hash;

    // Where in the list does this chunk belong?
    qint64 _chunk_index_location;

    // The actual bytes of the chunk
    // This may be empty if it hasn't been loaded yet
    QByteArray _chunk_bytes;

    // The locations where this chunk is stored
    QList<QString> _chunk_location_urls;

};

#endif // CM_SYNCFILECHUNK_H
