## -*- mode: html; coding: utf-8 -*-
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
  % if entity.club and entity.federation and entity.club is entity.federation:
  <dt>${_('Associated and federated with')}</dt>
  <dd>
    <a href="${request.route_path('lit_club', guid=entity.club.guid) | n}">${entity.club.description}</a>
  </dd>
  % else:
  % if entity.club:
  <dt>${_('Associated to')}</dt>
  <dd>
    <a href="${request.route_path('lit_club', guid=entity.club.guid) | n}">${entity.club.description}</a>
  </dd>
  % endif
  % if entity.federation:
  <dt>${_('Federated with')}</dt>
  <dd>
    <a href="${request.route_path('lit_club', guid=entity.federation.guid) | n}">${entity.federation.description}</a>
  </dd>
  % endif
  % endif
  % if partecipations:
  <dt>${_('Tourneys')}</dt>
  <dd>
    <%
        gold = silver = bronze = 0
        for p in partecipations:
            if p.rank == 1:
                gold += 1
            elif p.rank == 2:
                silver += 1
            elif p.rank == 3:
                bronze += 1
        if gold or silver or bronze:
            details = []
            if gold:
                details.append('<span class="winner">%s</span>' %
                               escape(ngettext('%d gold medal', '%d gold medals', gold) % gold))
            if silver:
                details.append(escape(ngettext('%d silver medal', '%d silver medals', silver) % silver))
            if bronze:
                details.append(escape(ngettext('%d bronze medal', '%d bronze medals', bronze) % bronze))
            details = ' (' + njoin(details) + ')'
        else:
            details = ''
    %>
    ${len(partecipations)}${details | n}
  </dd>
  <dt>${_('Matches')}</dt>
  <%
     wins, losts, ties = entity.matchesSummary()
     done = wins + losts + ties
     msgs = []
     if wins:
         wp = ' (%d%%)' % (100 * wins // done)
         msgs.append((ngettext('%d won', '%d won', wins) % wins) + wp)
     if losts:
         lp = ' (%d%%)' % (100 * losts // done)
         msgs.append((ngettext('%d lost', '%d lost', losts) % losts + lp))
     if ties:
         tp = ' (%d%%)' % (100 * ties // done)
         msgs.append((ngettext('%d tied', '%d tied', ties) % ties) + tp)
  %>
  <dd>${njoin(msgs)}</dd>
  % endif
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
        <a href="${request.route_path('lit_tourney', guid=row.tourney.guid) | n}">${row.tourney.description}</a>
      </td>
      <td class="championship">
        <a href="${request.route_path('lit_championship', guid=row.tourney.championship.guid) | n}" title="${samechampionship and _('Idem') or row.tourney.championship.club.description}">
          ${samechampionship and '...' or row.tourney.championship.description}
        </a>
      </td>
      <td class="date">${row.tourney.date.strftime(_('%m-%d-%Y'))}</td>
      % if team_events:
      <% players = [getattr(row, 'player%d'%i) for i in range(1,5) if getattr(row, 'idplayer%d'%i) not in (None, entity.idplayer)] %>
      <td class="player">
        ${njoin(players, stringify=lambda p: '<a href="%s">%s</a>' % (request.route_path('lit_player', guid=p.guid), escape(p.caption(html=False)))) | n}
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

% if partecipations:
<table class="ranking">
  <caption>${_('Tourneys results')}</caption>
  ${table_header()}
  ${table_body()}
</table>
% endif