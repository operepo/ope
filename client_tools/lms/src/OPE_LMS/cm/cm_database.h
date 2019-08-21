#ifndef CM_DATABASE_H
#define CM_DATABASE_H

#include <QObject>
#include <QtSql>

class CM_Database : public QObject
{
    Q_OBJECT
public:



    explicit CM_Database(QObject *parent = nullptr);

    static QSqlQuery *Query(QString sql);

    static bool DBConnect();
private:

    static bool _isDBConnected;
    static QSqlDatabase db;






signals:

public slots:


};

#endif // CM_DATABASE_H
