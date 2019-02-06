#ifndef CM_MIMETYPES_H
#define CM_MIMETYPES_H

#include <QObject>
#include <QHash>

class CM_MimeTypes : public QObject
{
    Q_OBJECT
public:
    explicit CM_MimeTypes(QObject *parent = nullptr);

    static QHash<QString,QString> mime_types;

signals:

public slots:

    static void LoadMimeTypes();

    static QString GetMimeType(QString ext);

    static QString GetExtentionForMimeType(QString mime_type);

};

#endif // CM_MIMETYPES_H
