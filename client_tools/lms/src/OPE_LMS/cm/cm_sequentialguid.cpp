#include "cm_sequentialguid.h"

// Declare static variables
bool CM_SequentialGUID::rand_init = false;


CM_SequentialGUID::CM_SequentialGUID(QObject *parent) :
    QObject(parent)
{
}

void CM_SequentialGUID::InitRand() {
    if (!rand_init) {
        QTime t = QTime::currentTime();
        qsrand((uint) t.msec());

        rand_init = true;
    }
}

int CM_SequentialGUID::randInt(int low, int high) {
    InitRand();
    return qrand() % ((high+1) - low) + low;
}

QUuid CM_SequentialGUID::GetSequentialGUID(SequentialGUIDType guid_type)
{
    QByteArray randBytes;
    // Get some random bytes
    for(int i=0; i<10; i++) {
        char b = (char)randInt(0, 255);
        randBytes.append(b);
    }
    // Would prefer a cryptographically secure rng
    // _rng.GetBytes(randBytes);


    //long timestamp = QDateTime::Now.Ticks / 10000L;
    qint64 timestamp = QDateTime::currentMSecsSinceEpoch();
    QByteArray timestampBytes;
    timestampBytes.resize(sizeof(timestamp));
    QByteArray timestampBytesRev;
    timestampBytesRev.resize(sizeof(timestamp));

    char *ptr = (char *)&timestamp;
    for(int i=0; i<8; i++) {
        timestampBytes[i] = ptr[i];
        timestampBytesRev[7-i] = ptr[i];
    }
    // We only want a total of 16 bytes (10 random, 6 timestamp),
    // cut off high bytes which should be 0's anyway
    // unless this is the future...
    timestampBytes.remove(6, 2);
    timestampBytesRev.remove(0,2);

    QByteArray tsBytes;

    // Use the correct endian so we get a proper sequence (e.g. counting up digits
    // on the right so it sorts properly in the database)
#if Q_BYTE_ORDER == Q_LITTLE_ENDIAN
    tsBytes = timestampBytesRev;
#else
    tsBytes = timestampBytes;
#endif

    QByteArray guidBytes;

    switch (guid_type) {
    case SequentialAsString:
    case SequentialAsBinary:
        guidBytes.append(tsBytes);
        guidBytes.append(randBytes);
        break;

    case SequentialAtEnd:
        guidBytes.append(randBytes);
        guidBytes.append(tsBytes);
        break;
    }

    QUuid uid = QUuid::fromRfc4122(guidBytes);
    return uid;
}
