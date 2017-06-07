#ifndef CM_USERS_H
#define CM_USERS_H

#include <QObject>
#include <QCryptographicHash>

#include "cm/cm_persistentobject.h"


class CM_Users : public CM_PersistentObject
{
    Q_OBJECT
public:
    explicit CM_Users();

    static bool AuthenticateUser(QString user_name, QString user_password);

    static CM_Users *CreateUser(QString user_name);

    bool isAdminUser();

    bool SetPassword(QString new_password);
signals:

public slots:

};

#endif // CM_USERS_H
