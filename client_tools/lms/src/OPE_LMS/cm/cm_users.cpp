#include "cm_users.h"

CM_Users::CM_Users()
{
    object_type = "user";
}


bool CM_Users::AuthenticateUser(QString user_name, QString user_password)
{
    bool ret = false;       

    CM_Users user;
    user.SetIDValue(user_name);
    user.LoadObjectInfo();

    // Hash the password
    QCryptographicHash *hash = new QCryptographicHash(QCryptographicHash::Sha1);
    hash->addData(user_password.toUtf8());
    QString hashed_password = hash->result().toBase64();
    delete hash;

    if (user.GetValue("password") == hashed_password) {
        ret = true;
    }

    return ret;
}

CM_Users *CM_Users::CreateUser(QString user_name)
{
    // Generate a new user
    CM_Users *ret = new CM_Users();
    ret->SetIDValue(user_name);
    ret->SetValue("name", user_name);

    return ret;
}

bool CM_Users::isAdminUser()
{
    //// TODO - Check roles for admin status
    ///
    return true;
}

bool CM_Users::SetPassword(QString new_password)
{
    bool ret = true;

    // Hash the password
    QCryptographicHash *hash = new QCryptographicHash(QCryptographicHash::Sha1);
    hash->addData(new_password.toUtf8());
    QString hashed_password = hash->result().toBase64();
    delete hash;

    SetValue("password", hashed_password);

    return ret;
}
