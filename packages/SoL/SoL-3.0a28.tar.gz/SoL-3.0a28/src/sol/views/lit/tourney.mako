## -*- coding: utf-8 -*-
## :Progetto:  SoL
## :Creato:    sab 13 dic 2008 16:34:51 CET
## :Autore:    Lele Gaifax <lele@metapensiero.it>
## :Licenza:   GNU General Public License version 3 or later
##

<%inherit file="base.mako" />

<%
from sol.models.utils import njoin
if entity.championship.playersperteam==1:
    subject = _('Player')
else:
    subject = _('Team')
%>

<%def name="title()">
  ${entity.description}
</%def>

<%def name="header()">
  ${parent.header()}
  <h2 class="subtitle centered">
    <a href="${request.route_path('lit_championship', guid=entity.championship.guid) | n}">${entity.championship.description}</a>
  </h2>
</%def>

<%def name="club_emblem(url='', href='')">
  <%
     if entity.championship.club.emblem:
         parent.club_emblem(url="/lit/emblem/%s" % entity.championship.club.emblem,
                            href=entity.championship.club.siteurl,
                            title=entity.championship.club.description)
  %>
</%def>


## Body

<dl>
  <dt>${_('Club')}</dt>
  <dd><a href="${request.route_path('lit_club', guid=entity.championship.club.guid) | n}">${entity.championship.club.description}</a></dd>
  <dt>${_('Location')}</dt> <dd>${entity.location}</dd>
  <dt>${_('Date')}</dt> <dd>${entity.date.strftime(_('%m-%d-%Y'))}</dd>
  % if turn is not None or player is not None:
  <dt>${_('Duration')}</dt> <dd>${ngettext('%d minute', '%d minutes', entity.duration) % entity.duration}</dd>
  <% cmethod = entity.__class__.__table__.c.couplings.info['dictionary'][entity.couplings] %>
  <dt>${_('Coupling method')}</dt> <dd>${_(cmethod)}</dd>
  % else:
  % endif
  <% pmethod = entity.championship.__class__.__table__.c.prizes.info['dictionary'][entity.championship.prizes] %>
  <dt>${_('Prize-giving method')}</dt> <dd>${_(pmethod)}</dd>
  % if entity.rating:
  <dt>${_('Rating')}</dt>
  <dd><a href="${request.route_path('lit_rating', guid=entity.rating.guid) | n}">${entity.rating.description}</a></dd>
  % endif
  % if turn is None:
  <dt>${_('Players')}</dt> <dd>${len(entity.ranking)}</dd>
  % endif
  % if entity.rankedturn:
  <dt>${_('Turns')}</dt>
  <dd>
    ${', '.join(['<a href="%s">%d</a>' % (request.route_path('lit_tourney', guid=entity.guid, _query=dict(turn=i)), i) for i in range(1,entity.rankedturn+1)]) | n}
    (<a href="${request.route_path('pdf_results', id=entity.guid, _query=dict(turn='all')) | n}">pdf</a>)
  </dd>
  % if turn is not None:
  <dt>${_('Ranked turn')}</dt>
  <dd>
    <a href="${request.route_path('lit_tourney', guid=entity.guid) | n}">
      ${entity.rankedturn}
    </a>
  </dd>
  % endif
  % endif
</dl>

% if turn is None and player is None:

<%def name="ranking_header()">
  <thead>
    <tr>
      <td class="rank-header">#</td>
      <td class="player-header">${subject}</td>
      % if entity.rankedturn:
      <td class="event-header">${_('Points')}</td>
      <td class="event-header">${_('Bucholz')}</td>
      <td class="event-header">${_('Net score')}</td>
      <td class="event-header">${_('Total score')}</td>
      % endif
      % if entity.prized:
      <td class="sortedby total-header">${_('Final prize')}</td>
      % endif
    </tr>
  </thead>
</%def>

<%def name="ranking_body(ranking)">
  <tbody>
    % for i, row in enumerate(ranking, 1):
    ${ranking_row(i, row)}
    % endfor
  </tbody>
</%def>

<%def name="ranking_row(rank, row)">
    <tr class="${rank%2 and 'odd' or 'even'}-row">
      <td class="rank">${rank}</td>
      <% players = [getattr(row, 'player%d'%i) for i in range(1,5) if getattr(row, 'player%d'%i) is not None] %>
      <td class="player">${njoin(players, stringify=lambda p: '<a href="%s">%s</a>' % (request.route_path('lit_player', guid=p.guid), escape(p.caption(html=False)))) | n}</td>
      % if entity.rankedturn:
      <td class="event">${row.points}</td>
      <td class="event">${row.bucholz}</td>
      <td class="event">${row.netscore}</td>
      <td class="event">${row.totscore}</td>
      % endif
      % if entity.prized:
      <td class="sortedby total">${row.prize}</td>
      % endif
    </tr>
</%def>

<% ranking = entity.ranking %>
<table class="ranking">
  <caption>
  % if entity.prized or entity.date <= today:
  ${_('Ranking')} (<a href="${request.route_path('pdf_ranking', id=entity.guid) | n}">pdf</a>)
  % endif
  </caption>
  ${ranking_header()}
  ${ranking_body(ranking)}
</table>

% else:

<%def name="matches_header()">
  <thead>
    <tr>
      <td class="rank-header">#</td>
      <td colspan="3" class="competitors-header">${_('Competitors')}</td>
      <td colspan="3" class="scores-header">${_('Score')}</td>
    </tr>
  </thead>
</%def>

<%def name="matches_body(matches)">
  <tbody>
    % for i, row in enumerate(matches, 1):
    ${matches_row(i, row)}
    % endfor
  </tbody>
</%def>

<%def name="matches_row(rank, row)">
    <tr class="${rank%2 and 'odd' or 'even'}-row">
      <td class="rank">${rank}</td>
      <%
         ctor = row.competitor1
         players = [ctor.player1, ctor.player2, ctor.player3, ctor.player4]
      %>

      <td class="competitor1${row.score1>row.score2 and ' winner' or ''}">
        ${njoin(players, stringify=lambda p: '<a href="%s" title="%s">%s</a>' % (
            request.route_path('lit_tourney', guid=row.tourney.guid, _query=dict(player=p.guid)),
            escape(_('Show matches played by %s') % p.caption(html=False)),
            escape(p.caption(html=False)))) | n}
      </td>
      <td class="separator"></td>
      % if row.idcompetitor2:
      <%
         ctor = row.competitor2
         players = [ctor.player1, ctor.player2, ctor.player3, ctor.player4]
      %>
      <td class="competitor2${row.score1<row.score2 and ' winner' or ''}">
        ${njoin(players, stringify=lambda p: '<a href="%s" title="%s">%s</a>' % (
            request.route_path('lit_tourney', guid=row.tourney.guid, _query=dict(player=p.guid)),
            escape(_('Show matches played by %s') % p.caption(html=False)),
            escape(p.caption(html=False)))) | n}
      </td>
      % else:
      <td class="phantom">${_('Phantom')}</td>
      % endif
      <td class="score1${row.score1>row.score2 and ' winner' or ''}">${row.score1}</td>
      <td class="separator"></td>
      <td class="score2${row.score1<row.score2 and ' winner' or ''}">${row.score2}</td>
    </tr>
</%def>

<%
   if player:
       matches = [m for m in entity.matches
                  if (m.competitor1.player1.guid == player or
                      m.competitor1.player2 and m.competitor1.player2.guid == player or
                      m.competitor1.player3 and m.competitor1.player3.guid == player or
                      m.competitor1.player4 and m.competitor1.player4.guid == player or
                      (m.competitor2 and (m.competitor2.player1.guid == player or
                                          m.competitor2.player2 and m.competitor2.player2.guid == player or
                                          m.competitor2.player3 and m.competitor2.player3.guid == player or
                                          m.competitor2.player4 and m.competitor2.player4.guid == player)))]
       if matches:
           m0 = matches[0]
           if (m0.competitor1.player1.guid == player or
               m0.competitor1.player2 and m0.competitor1.player2.guid == player or
               m0.competitor1.player3 and m0.competitor1.player3.guid == player or
               m0.competitor1.player4 and m0.competitor1.player4.guid == player):
               cname = m0.competitor1.caption(html=False)
           else:
               cname = m0.competitor2.caption(html=False)
           caption = _('Matches played by %s') % (
               '<a href="%s">%s</a>' % (request.route_path('lit_player', guid=player), escape(cname)))
       else:
           caption = _('No matches for this player')
   else:
       matches = [m for m in entity.matches if m.turn == int(turn)]
       caption = _('Turn no. %s (%s)') % (
           turn, '<a href="%s">pdf</a>' % (request.route_path('pdf_results', id=entity.guid,
                                                              _query=dict(turn=turn))))
%>

<table class="matches">
  <caption>${caption | n}</caption>
  ${matches_header()}
  ${matches_body(matches)}
</table>

% endif
