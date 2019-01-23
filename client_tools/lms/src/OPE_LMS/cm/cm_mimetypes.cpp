#include "cm_mimetypes.h"

QHash<QString,QString> CM_MimeTypes::mime_types;

CM_MimeTypes::CM_MimeTypes(QObject *parent) :
    QObject(parent)
{
}


void CM_MimeTypes::LoadMimeTypes()
{
    mime_types["html"] = "text/html";
    mime_types["htm"] = "text/html";

    mime_types["text"] = "text/text";
    mime_types["txt"] = "text/text";

    mime_types["jpg"] = "image/jpeg";
    mime_types["jpeg"] = "image/jpeg";

    mime_types["png"] = "image/png";\

    mime_types["gif"] = "image/gif";

    mime_types["tif"] = "image/tiff";
    mime_types["tiff"] = "image/tiff";

    mime_types["xml"] = "text/xml";
    mime_types["svg"] = "text/xml";
    mime_types["css"] = "text/css";

    mime_types["java"] = "application/java";

    mime_types["swf"] = "application/x-shockwave-flash";
    mime_types["flv"] = "application/x-shockwave-flash";

    mime_types["wav"] = "audio/x-wav";

    mime_types["avi"] = "video/x-msvideo";

    mime_types["mp4"] = "video/mp4";

    mime_types["mp3"] = "audio/mpeg";

    mime_types["ogg"] = "application/ogg";

    mime_types["zip"] = "application/octet-stream";
    mime_types["rar"] = "application/octet-stream";

    mime_types["doc"] = "application/msword";
    mime_types["docx"] = "application/msword";

    mime_types["xls"] = "application/excel";
    mime_types["xlsx"] = "application/excel";

    mime_types["pdf"] = "application/pdf";
}


QString CM_MimeTypes::GetMimeType(QString ext)
{
    if (mime_types.count() < 1) { LoadMimeTypes(); }

    QString ret = mime_types[ext];
    if (ret == "") { ret = "application/octet-stream"; }

    return ret;
}
