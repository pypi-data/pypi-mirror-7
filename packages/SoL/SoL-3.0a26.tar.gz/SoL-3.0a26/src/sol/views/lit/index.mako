## -*- coding: utf-8 -*-
## :Progetto:  SoL
## :Creato:    mer 17 dic 2008 02:16:28 CET
## :Autore:    Lele Gaifax <lele@metapensiero.it>
## :Licenza:   GNU General Public License version 3 or later
##

<%inherit file="base.mako" />

<%
from operator import attrgetter
%>

<%def name="title()">
  ${_('SoL Lit')}
</%def>

## Body

<dl>
  <dt>${_('Clubs')}</dt>
  <dd>
    ${nclubs}
    (${ngettext('%d country', '%d countries', nccountries) % nccountries})
  </dd>
  <dt>${_('Federations')}</dt> <dd>${nfederations}</dd>
  <dt>${_('Championships')}</dt> <dd>${nchampionships}</dd>
  <dt>${_('Tourneys')}</dt> <dd>${ntourneys}</dd>
  <dt>${_('Players')}</dt>
  <dd>
    ${nplayers}
    (${ngettext('%d country', '%d countries', npcountries) % npcountries})
  </dd>
  <dt>${_('Ratings')}</dt> <dd>${nratings}</dd>
</dl>

<div class="centered multi-columns">
% for index, (country, code) in enumerate(sorted(clubsbycountry)):
  <h3>
    % if code:
    <img src="/static/images/flags/${code}.png" />
    % endif
    ${country}
  </h3>
  % for club in sorted(clubsbycountry[(country, code)], key=attrgetter('description')):
  <p class="${'federation' if club.isfederation else 'club'}">
    <a href="club?club=${club.guid}">${club.description}</a>
    <% nc = len(club.championships) %>
    (${ngettext('%d championship', '%d championships', nc) % nc})
  </p>
  % endfor
  </ul>
% endfor
</div>

##% if clubs:
##<h3>${_('Clubs')}</h3>
##% endif
##
##% for club in clubs:
##<div class="club">
##  % if club.emblem:
##  <img class="emblem centered" src="/lit/emblem/${club.emblem}" />
##  % else:
##  <span class="spacer">&nbsp;</span>
##  % endif
##
##  <h4 class="centered">
##    % if club.siteurl:
##    <a href="${club.siteurl}" target="_blank">
##    % endif
##    ${club.description}
##    % if club.siteurl:
##    </a>
##    % endif
##  % if club.nationality:
##    (<img src="/static/images/flags/${club.nationality}.png" />
##    ${club.nationality})
##  % endif
##  </h4>
##
##  <%
##     singles = []
##     doubles = []
##     teams = []
##     future = []
##     for championship in club.championships:
##         pt = []
##         for t in championship.tourneys:
##             if t.prized:
##                 pt.append(t)
##             elif t.date>today:
##                 future.append(t)
##         nt = len(pt)
##         if nt:
##             new = (today - pt[-1].date).days < 21
##             if championship.playersperteam == 1:
##                 singles.append((championship, nt, new))
##             elif championship.playersperteam == 2:
##                 doubles.append((championship, nt, new))
##             else:
##                 teams.append((championship, nt, new))
##  %>
##  % if singles:
##  <h5>${_('Singles')}</h5>
##  <ol>
##    % for championship,nt,new in singles:
##    <li class="championship">
##      <a href="championship?championship=${championship.guid}">
##        ${championship.description}
##      </a>
##      (${ngettext('%d tourney', '%d tourneys', nt) % nt})
##      % if new:
##      <img src="/static/images/new.png" />
##      % endif
##    </li>
##    % endfor
##  </ol>
##  % endif
##  % if doubles:
##  <h5>${_('Doubles')}</h5>
##  <ol>
##    % for championship,nt,new in doubles:
##    <li class="championship">
##      <a href="championship?championship=${championship.guid}">
##        ${championship.description}
##      </a>
##      (${ngettext('%d tourney', '%d tourneys', nt) % nt})
##      % if new:
##      <img src="/static/images/new.png" />
##      % endif
##    </li>
##    % endfor
##  </ol>
##  % endif
##  % if teams:
##  <h5>${_('Teams')}</h5>
##  <ol>
##    % for championship,nt,new in teams:
##    <li class="championship">
##      <a href="championship?championship=${championship.guid}">
##        ${championship.description}
##      </a>
##      (${ngettext('%d tourney', '%d tourneys', nt) % nt})
##      % if new:
##      <img src="/static/images/new.png" />
##      % endif
##    </li>
##    % endfor
##  </ol>
##  % endif
##</div>
##% endfor
##
##<div class="clear" />
