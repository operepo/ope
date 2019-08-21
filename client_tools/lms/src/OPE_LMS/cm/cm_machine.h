#ifndef CM_MACHINE_H
#define CM_MACHINE_H

#include <QObject>
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QVariant>
#include <QNetworkInterface>
#include <QUuid>
#include <QCryptographicHash>

//#include <QMessageBox>


#include "cm_sequentialguid.h"


class CM_Machine : public QObject
{
    Q_OBJECT
public:
    explicit CM_Machine(QObject *parent = nullptr);
    
    // Make sure that the machines data is setup properly
    void InitDB();

    void CalculateMachineID();

    bool IsNetworkActive();

signals:

public slots:

private:

    // Use machine info to figure out possible unique ids for this system
    void CalculatePossibleMachineIDs();

    QString con_string;
    bool db_init;
    bool db_connected;


    QList<QString> possible_machine_ids;
    QList<QString> mac_addresses;
    QString machine_id;

};

#endif // CM_MACHINE_H
