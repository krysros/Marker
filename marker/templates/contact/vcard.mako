<%!
    def vescape(text):
        """Escape special characters for vCard TEXT values (RFC 6350)."""
        return (
            str(text)
            .replace("\\", "\\\\")
            .replace(",", "\\,")
            .replace(";", "\\;")
            .replace("\r\n", "\\n")
            .replace("\r", "\\n")
            .replace("\n", "\\n")
        )
%>\
BEGIN:VCARD
VERSION:4.0
FN:${contact.name | vescape}
N:${contact.name | vescape};;;;
% if contact.role:
TITLE:${contact.role | vescape}
ROLE:${contact.role | vescape}
% endif
% if contact.phone:
TEL;TYPE=WORK;VALUE=uri:tel:${contact.phone | vescape}
% endif
% if contact.email:
EMAIL;TYPE=WORK:${contact.email | vescape}
% endif
% if contact.company:
<%
  co = contact.company
  has_adr = any([co.street, co.city, co.postcode, co.country, co.subdivision])
%>
ORG:${contact.company.name | vescape}
% if has_adr:
ADR;TYPE=WORK:;;${(co.street or "") | vescape};${(co.city or "") | vescape};${(co.subdivision or "") | vescape};${(co.postcode or "") | vescape};${(co.country or "") | vescape}
% endif
% if co.website:
URL;TYPE=WORK:${co.website | vescape}
% endif
% if co.NIP:
X-NIP:${co.NIP | vescape}
% endif
% if co.REGON:
X-REGON:${co.REGON | vescape}
% endif
% if co.KRS:
X-KRS:${co.KRS | vescape}
% endif
% elif contact.project:
<%
  proj = contact.project
  has_padr = any([proj.street, proj.city, proj.postcode, proj.country, proj.subdivision])
%>
ORG:${contact.project.name | vescape}
% if has_padr:
ADR;TYPE=WORK:;;${(proj.street or "") | vescape};${(proj.city or "") | vescape};${(proj.subdivision or "") | vescape};${(proj.postcode or "") | vescape};${(proj.country or "") | vescape}
% endif
% if proj.website:
URL;TYPE=WORK:${proj.website | vescape}
% endif
% endif
% if contact.updated_at:
REV:${contact.updated_at.strftime('%Y%m%dT%H%M%SZ')}
% elif contact.created_at:
REV:${contact.created_at.strftime('%Y%m%dT%H%M%SZ')}
% endif
UID:urn:uuid:contact-${contact.id}
END:VCARD
