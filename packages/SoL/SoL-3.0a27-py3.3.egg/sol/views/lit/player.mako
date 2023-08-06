## -*- coding: utf-8 -*-
## :Progetto:  SoL
## :Creato:    sab 13 dic 2008 16:32:24 CET
## :Autore:    Lele Gaifax <lele@metapensiero.it>
## :Licenza:   GNU General Public License version 3 or later
##

<%inherit file="base.mako" />

<%
from sol.models.utils import njoin
%>

<%def name="title()">
  ${entity.caption(html=False)}
</%def>

<%def name="club_emblem(url='', href='')">
  <%
     if entity.idclub is not None and entity.club.emblem:
         parent.club_emblem(url="/lit/emblem/%s" % entity.club.emblem,
                            href=entity.club.siteurl,
                            title=entity.club.description)
  %>
</%def>

## Body

% if entity.portrait:
<img class="centered portrait" src="/lit/portrait/${entity.portrait}" />
% endif

<%
partecipations = entity.partecipations()
team_events = any(c.idplayer2 is not None for c in partecipations)
%>

<dl>
  <dt>${_('First name')}</dt> <dd>${entity.firstname}</dd>
  <dt>${_('Last name')}</dt> <dd>${entity.lastname}</dd>
  % if not entity.shouldOmitNickName():
  <dt>${_('Nickname')}</dt> <dd>${entity.nickname}</dd>
  % endif
  % if entity.sex:
  <% sex = entity.__class__.__table__.c.sex.info['dictionary'][entity.sex] %>
  <dt>${_('Sex')}</dt> <dd>${_(sex)}</dd>
  % endif
  % if entity.nationality:
  <dt>${_('Country')}</dt>
  <dd>
    <img src="/static/images/flags/${entity.nationality}.png" />
    ${entity.country}
    % if entity.citizenship:
    (${_('citizenship')})
    % endif
  </dd>
  % endif
  % if entity.club:
  <dt>${_('Associated to')}</dt>
  <dd><a href="club?club=${entity.club.guid}">${entity.club.description}</a></dd>
  % endif
  % if entity.federation:
  <dt>${_('Federated with')}</dt>
  <dd><a href="club?club=${entity.federation.guid}">${entity.federation.description}</a></dd>
  % endif
  <dt>${_('Tourneys')}</dt> <dd>${len(partecipations)}</dd>
  <dt>${_('Matches')}</dt>
  <%
     wins, losts, ties = entity.matchesSummary()
     done = wins + losts + ties
     msgs = []
     if wins:
         wp = ' (%d%%)' % (100 * wins // done)
         msgs.append((ngettext('%d win', '%d wins', wins) % wins) + wp)
     if losts:
         lp = ' (%d%%)' % (100 * losts // done)
         msgs.append((ngettext('%d lost', '%d losts', losts) % losts + lp))
     if ties:
         tp = ' (%d%%)' % (100 * ties // done)
         msgs.append((ngettext('%d tie', '%d ties', ties) % ties) + tp)
  %>
  <dd>${njoin(msgs)}</dd>
</dl>

<%def name="table_header()">
      <thead>
        <tr>
          <td class="rank-header">#</td>
          <td class="tourney-header">${_('Tourney')}</td>
          <td class="championship-header">${_('Championship')}</td>
          <td class="date-header">${_('Date')}</td>
          % if team_events:
          <td class="player-header">${_('In team with')}</td>
          % endif
          <td class="event-header">${_('Points')}</td>
          <td class="event-header">${_('Bucholz')}</td>
          <td class="event-header">${_('Net score')}</td>
          <td class="event-header">${_('Total score')}</td>
          <td class="sortedby total-header">${_('Final prize')}</td>
          <td class="sortedby total-header">${_('Rank')}</td>
        </tr>
      </thead>
</%def>

<%def name="table_body()">
      <tbody>
        <% prevs = None %>
        % for i, row in enumerate(partecipations, 1):
        ${table_row(i, row, row.tourney.championship is prevs)}
        <% prevs = row.tourney.championship %>
        % endfor
      </tbody>
</%def>

<%def name="table_row(index, row, samechampionship)">
        <tr class="${index%2 and 'odd' or 'even'}-row${' winner' if row.rank==1 else ''}">
          <td class="index">${index}</td>
          <td class="tourney">
            <a href="tourney?tourney=${row.tourney.guid}">${row.tourney.description}</a>
          </td>
          <td class="championship">
            <a href="championship?championship=${row.tourney.championship.guid}" title="${samechampionship and _('Idem') or row.tourney.championship.club.description}">
              ${samechampionship and '...' or row.tourney.championship.description}
            </a>
          </td>
          <td class="date">${row.tourney.date.strftime(_('%m-%d-%Y'))}</td>
          % if team_events:
          <% players = [getattr(row, 'player%d'%i) for i in range(1,5) if getattr(row, 'idplayer%d'%i) not in (None, entity.idplayer)] %>
          <td class="player">
            ${njoin(players, stringify=lambda p: '<a href="player?player=%s">%s</a>' % (p.guid, escape(p.caption(html=False)))) | n}
          </td>
          % endif
          <td class="event">${row.points}</td>
          <td class="event">${row.bucholz}</td>
          <td class="event">${row.netscore}</td>
          <td class="event">${row.totscore}</td>
          <td class="sortedby total">${row.prize}</td>
          <td class="sortedby total">${row.rank}</td>
        </tr>
</%def>

<table class="ranking">
  <caption>${_('Tourneys results')}</caption>
  ${table_header()}
  ${table_body()}
</table>
