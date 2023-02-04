BEGIN:VCARD
VERSION:4.0
FN:${person.name}
% if person.role:
ROLE:${person.role}
% endif
% if person.phone:
TEL;TYPE=work,voice;VALUE=uri:tel:${person.phone}
% endif
% if person.email:
EMAIL;TYPE=work:${person.email}
% endif
% if person.company:
ORG;TYPE=work:${person.company.name}
% endif
END:VCARD