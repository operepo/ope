#ifndef CM_SEQUENTIALGUID_H
#define CM_SEQUENTIALGUID_H

#include <QObject>
#include <QUuid>
#include <QByteArray>
#include <QDateTime>
#include <QDataStream>
#include <QTime>
#include <QRandomGenerator>



class CM_SequentialGUID : public QObject
{
    Q_OBJECT
public:
//    Q_INVOKABLE QUuid getSequentialGUID() const {
//        return CM_SequentialGUID::GetSequentialGUID(SequentialAsString);
//    }

    explicit CM_SequentialGUID(QObject *parent = nullptr);
    
    enum SequentialGUIDType {
        SequentialAsString = 0,
        SequentialAsBinary = 1,
        SequentialAtEnd = 2
    };

    static QUuid GetSequentialGUID(SequentialGUIDType guid_type);


signals:

public slots:

private:
    static void InitRand();
    static int randInt(int low, int high);

    static bool rand_init;

};

#endif // CM_SEQUENTIALGUID_H
