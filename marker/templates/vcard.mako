<%!
    def vescape(text):
        return text.replace('"', '').replace("'", "").replace('\\', '\\\\').replace(';', '_').replace(':', '_').replace('&', '_')
%>
BEGIN:VCARD
VERSION:4.0
FN:${contact.name | vescape}
% if contact.role:
ROLE:${contact.role | vescape}
% endif
% if contact.phone:
TEL;TYPE=work,voice;VALUE=uri:tel:${contact.phone | vescape}
% endif
% if contact.email:
EMAIL;TYPE=work:${contact.email | vescape}
% endif
% if contact.company:
ORG;TYPE=work:${contact.company.name | vescape}
% endif
END:VCARD