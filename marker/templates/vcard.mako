BEGIN:VCARD
VERSION:4.0
FN:${contact.name}
% if contact.role:
ROLE:${contact.role}
% endif
% if contact.phone:
TEL;TYPE=work,voice;VALUE=uri:tel:${contact.phone}
% endif
% if contact.email:
EMAIL;TYPE=work:${contact.email}
% endif
% if contact.company:
ORG;TYPE=work:${contact.company.name}
% endif
END:VCARD