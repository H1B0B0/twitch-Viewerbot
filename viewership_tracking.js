!(function () {
  try {
    var e =
        "undefined" != typeof window
          ? window
          : "undefined" != typeof global
          ? global
          : "undefined" != typeof self
          ? self
          : {},
      i = new e.Error().stack;
    i &&
      ((e._sentryDebugIds = e._sentryDebugIds || {}),
      (e._sentryDebugIds[i] = "aaf61e67-3d45-4785-99c5-8400658ef278"),
      (e._sentryDebugIdIdentifier =
        "sentry-dbid-aaf61e67-3d45-4785-99c5-8400658ef278"));
  } catch (e) {}
})(),
  (self.webpackChunktwitch_twilight =
    self.webpackChunktwitch_twilight || []).push([
    [38923],
    {
      428728: function (e) {
        var i = {
          kind: "Document",
          definitions: [
            {
              kind: "OperationDefinition",
              operation: "query",
              name: { kind: "Name", value: "GuestStarSessionID" },
              variableDefinitions: [
                {
                  kind: "VariableDefinition",
                  variable: {
                    kind: "Variable",
                    name: { kind: "Name", value: "channelLogin" },
                  },
                  type: {
                    kind: "NonNullType",
                    type: {
                      kind: "NamedType",
                      name: { kind: "Name", value: "String" },
                    },
                  },
                  directives: [],
                },
              ],
              directives: [],
              selectionSet: {
                kind: "SelectionSet",
                selections: [
                  {
                    kind: "Field",
                    name: { kind: "Name", value: "channel" },
                    arguments: [
                      {
                        kind: "Argument",
                        name: { kind: "Name", value: "name" },
                        value: {
                          kind: "Variable",
                          name: { kind: "Name", value: "channelLogin" },
                        },
                      },
                    ],
                    directives: [],
                    selectionSet: {
                      kind: "SelectionSet",
                      selections: [
                        {
                          kind: "Field",
                          name: { kind: "Name", value: "id" },
                          arguments: [],
                          directives: [],
                        },
                        {
                          kind: "Field",
                          name: { kind: "Name", value: "guestStarSessionCall" },
                          arguments: [],
                          directives: [],
                          selectionSet: {
                            kind: "SelectionSet",
                            selections: [
                              {
                                kind: "Field",
                                name: { kind: "Name", value: "id" },
                                arguments: [],
                                directives: [],
                              },
                            ],
                          },
                        },
                      ],
                    },
                  },
                ],
              },
            },
          ],
        };
        function n(e, i) {
          if ("FragmentSpread" === e.kind) i.add(e.name.value);
          else if ("VariableDefinition" === e.kind) {
            var a = e.type;
            "NamedType" === a.kind && i.add(a.name.value);
          }
          e.selectionSet &&
            e.selectionSet.selections.forEach(function (e) {
              n(e, i);
            }),
            e.variableDefinitions &&
              e.variableDefinitions.forEach(function (e) {
                n(e, i);
              }),
            e.definitions &&
              e.definitions.forEach(function (e) {
                n(e, i);
              });
        }
        var a = {};
        i.definitions.forEach(function (e) {
          if (e.name) {
            var i = new Set();
            n(e, i), (a[e.name.value] = i);
          }
        }),
          (e.exports = i);
      },
      525513: function (e) {
        var i = {
          kind: "Document",
          definitions: [
            {
              kind: "OperationDefinition",
              operation: "query",
              name: { kind: "Name", value: "GetUserIDFromLogin" },
              variableDefinitions: [
                {
                  kind: "VariableDefinition",
                  variable: {
                    kind: "Variable",
                    name: { kind: "Name", value: "login" },
                  },
                  type: {
                    kind: "NonNullType",
                    type: {
                      kind: "NamedType",
                      name: { kind: "Name", value: "String" },
                    },
                  },
                  directives: [],
                },
                {
                  kind: "VariableDefinition",
                  variable: {
                    kind: "Variable",
                    name: { kind: "Name", value: "lookupType" },
                  },
                  type: {
                    kind: "NonNullType",
                    type: {
                      kind: "NamedType",
                      name: { kind: "Name", value: "UserLookupType" },
                    },
                  },
                  directives: [],
                },
              ],
              directives: [],
              selectionSet: {
                kind: "SelectionSet",
                selections: [
                  {
                    kind: "Field",
                    name: { kind: "Name", value: "user" },
                    arguments: [
                      {
                        kind: "Argument",
                        name: { kind: "Name", value: "login" },
                        value: {
                          kind: "Variable",
                          name: { kind: "Name", value: "login" },
                        },
                      },
                      {
                        kind: "Argument",
                        name: { kind: "Name", value: "lookupType" },
                        value: {
                          kind: "Variable",
                          name: { kind: "Name", value: "lookupType" },
                        },
                      },
                    ],
                    directives: [],
                    selectionSet: {
                      kind: "SelectionSet",
                      selections: [
                        {
                          kind: "Field",
                          name: { kind: "Name", value: "id" },
                          arguments: [],
                          directives: [],
                        },
                      ],
                    },
                  },
                ],
              },
            },
          ],
        };
        function n(e, i) {
          if ("FragmentSpread" === e.kind) i.add(e.name.value);
          else if ("VariableDefinition" === e.kind) {
            var a = e.type;
            "NamedType" === a.kind && i.add(a.name.value);
          }
          e.selectionSet &&
            e.selectionSet.selections.forEach(function (e) {
              n(e, i);
            }),
            e.variableDefinitions &&
              e.variableDefinitions.forEach(function (e) {
                n(e, i);
              }),
            e.definitions &&
              e.definitions.forEach(function (e) {
                n(e, i);
              });
        }
        var a = {};
        i.definitions.forEach(function (e) {
          if (e.name) {
            var i = new Set();
            n(e, i), (a[e.name.value] = i);
          }
        }),
          (e.exports = i);
      },
      828301: function (e) {
        e.exports = {
          kind: "Document",
          definitions: [
            {
              kind: "FragmentDefinition",
              name: { kind: "Name", value: "sharedChatParticipant" },
              typeCondition: {
                kind: "NamedType",
                name: { kind: "Name", value: "SharedChatParticipant" },
              },
              directives: [],
              selectionSet: {
                kind: "SelectionSet",
                selections: [
                  {
                    kind: "Field",
                    name: { kind: "Name", value: "id" },
                    arguments: [],
                    directives: [],
                  },
                  {
                    kind: "Field",
                    name: { kind: "Name", value: "channel" },
                    arguments: [],
                    directives: [],
                    selectionSet: {
                      kind: "SelectionSet",
                      selections: [
                        {
                          kind: "Field",
                          name: { kind: "Name", value: "id" },
                          arguments: [],
                          directives: [],
                        },
                      ],
                    },
                  },
                  {
                    kind: "Field",
                    name: { kind: "Name", value: "autoAcceptsAt" },
                    arguments: [],
                    directives: [],
                  },
                  {
                    kind: "Field",
                    name: { kind: "Name", value: "status" },
                    arguments: [],
                    directives: [],
                  },
                ],
              },
            },
          ],
        };
      },
      297745: function (e, i, n) {
        var a = {
            kind: "Document",
            definitions: [
              {
                kind: "OperationDefinition",
                operation: "query",
                name: { kind: "Name", value: "SharedChatSession" },
                variableDefinitions: [
                  {
                    kind: "VariableDefinition",
                    variable: {
                      kind: "Variable",
                      name: { kind: "Name", value: "channelID" },
                    },
                    type: {
                      kind: "NonNullType",
                      type: {
                        kind: "NamedType",
                        name: { kind: "Name", value: "ID" },
                      },
                    },
                    directives: [],
                  },
                ],
                directives: [],
                selectionSet: {
                  kind: "SelectionSet",
                  selections: [
                    {
                      kind: "Field",
                      name: { kind: "Name", value: "sharedChatSession" },
                      arguments: [
                        {
                          kind: "Argument",
                          name: { kind: "Name", value: "channelID" },
                          value: {
                            kind: "Variable",
                            name: { kind: "Name", value: "channelID" },
                          },
                        },
                      ],
                      directives: [],
                      selectionSet: {
                        kind: "SelectionSet",
                        selections: [
                          {
                            kind: "Field",
                            name: { kind: "Name", value: "id" },
                            arguments: [],
                            directives: [],
                          },
                          {
                            kind: "Field",
                            name: { kind: "Name", value: "host" },
                            arguments: [],
                            directives: [],
                            selectionSet: {
                              kind: "SelectionSet",
                              selections: [
                                {
                                  kind: "Field",
                                  name: { kind: "Name", value: "id" },
                                  arguments: [],
                                  directives: [],
                                },
                              ],
                            },
                          },
                          {
                            kind: "Field",
                            name: { kind: "Name", value: "status" },
                            arguments: [],
                            directives: [],
                          },
                          {
                            kind: "Field",
                            name: { kind: "Name", value: "participants" },
                            arguments: [],
                            directives: [],
                            selectionSet: {
                              kind: "SelectionSet",
                              selections: [
                                {
                                  kind: "FragmentSpread",
                                  name: {
                                    kind: "Name",
                                    value: "sharedChatParticipant",
                                  },
                                  directives: [],
                                },
                              ],
                            },
                          },
                          {
                            kind: "Field",
                            name: { kind: "Name", value: "createdAt" },
                            arguments: [],
                            directives: [],
                          },
                          {
                            kind: "Field",
                            name: { kind: "Name", value: "updatedAt" },
                            arguments: [],
                            directives: [],
                          },
                          {
                            kind: "Field",
                            name: { kind: "Name", value: "autoStartsAt" },
                            arguments: [],
                            directives: [],
                          },
                        ],
                      },
                    },
                  ],
                },
              },
            ],
          },
          t = {};
        function d(e, i) {
          if ("FragmentSpread" === e.kind) i.add(e.name.value);
          else if ("VariableDefinition" === e.kind) {
            var n = e.type;
            "NamedType" === n.kind && i.add(n.name.value);
          }
          e.selectionSet &&
            e.selectionSet.selections.forEach(function (e) {
              d(e, i);
            }),
            e.variableDefinitions &&
              e.variableDefinitions.forEach(function (e) {
                d(e, i);
              }),
            e.definitions &&
              e.definitions.forEach(function (e) {
                d(e, i);
              });
        }
        a.definitions = a.definitions.concat(
          n(828301).definitions.filter(function (e) {
            if ("FragmentDefinition" !== e.kind) return !0;
            var i = e.name.value;
            return !t[i] && ((t[i] = !0), !0);
          })
        );
        var l = {};
        a.definitions.forEach(function (e) {
          if (e.name) {
            var i = new Set();
            d(e, i), (l[e.name.value] = i);
          }
        }),
          (e.exports = a);
      },
      321791: function (e, i, n) {
        "use strict";
        n.r(i),
          n.d(i, {
            SharedViewershipTracking: function () {
              return v;
            },
          });
        var a = n(296540),
          t = n(783321),
          d = n(290942),
          l = n(267924),
          r = n(894170),
          o = n(268385),
          s = n(554983),
          u = n(297745),
          c = n.n(u),
          v = function (e) {
            var i,
              n,
              u = e.channelLogin,
              v = null !== (i = (0, s.C)(u).userID) && void 0 !== i ? i : "",
              m = (0, t.IT)(c(), {
                skip: !v,
                variables: { channelID: v },
              }).data,
              k = (0, o.f)(u),
              f =
                null === (n = null == m ? void 0 : m.sharedChatSession) ||
                void 0 === n
                  ? void 0
                  : n.participants,
              S = (0, d.Z)(f);
            return (
              (0, a.useEffect)(
                function () {
                  var e;
                  (null == S ? void 0 : S.length) !==
                    (null == f ? void 0 : f.length) &&
                    (null === (e = null == m ? void 0 : m.sharedChatSession) ||
                    void 0 === e
                      ? void 0
                      : e.status) === l.gl3.ACTIVE &&
                    (null == f ||
                      f.forEach(function (e) {
                        var i, n, a;
                        !(null == S
                          ? void 0
                          : S.find(function (i) {
                              return i.id === e.id;
                            })) &&
                          r.E5.track("shared_viewership_client_video_play", {
                            channel_id:
                              null === (i = e.channel) || void 0 === i
                                ? void 0
                                : i.id,
                            guest_star_session_id:
                              null == k ? void 0 : k.sessionID,
                            shared_chat_session_id:
                              null === (n = m.sharedChatSession) || void 0 === n
                                ? void 0
                                : n.id,
                            is_channel_viewed_collaborator:
                              (null === (a = e.channel) || void 0 === a
                                ? void 0
                                : a.id) === v,
                          });
                      }));
                },
                [m, S, f, k, v]
              ),
              null
            );
          };
      },
      268385: function (e, i, n) {
        "use strict";
        n.d(i, {
          f: function () {
            return c;
          },
        });
        var a = n(973421),
          t = n.n(a),
          d = n(611407),
          l = n(783321),
          r = n(982821),
          o = n(456450),
          s = n(428728),
          u = n.n(s),
          c = function (e, i, n, a) {
            var s,
              c,
              v = (0, l.IT)(u(), {
                variables: { channelLogin: e || "" },
                skip: !e,
                fetchPolicy: a ? "network-only" : "cache-first",
              }),
              m = v.data,
              k = v.loading;
            return (
              (0, d.C)({
                query: u(),
                variables: { channelLogin: e },
                skip: !i || !n,
                topic: (0, o.O8)(i || ""),
                types: [r.PD.GuestStarCallStarted, r.PD.GuestStartCallEnded],
                mutator: function (e, i) {
                  switch (e.type) {
                    case r.PD.GuestStarCallStarted:
                      return t()(
                        i,
                        function (e) {
                          var i;
                          return null === (i = e.channel) || void 0 === i
                            ? void 0
                            : i.guestStarSessionCall;
                        },
                        function () {
                          return {
                            __typename: "GuestStarSessionForViewers",
                            id: e.data.session_id,
                          };
                        }
                      );
                    case r.PD.GuestStartCallEnded:
                      return t()(
                        i,
                        function (e) {
                          var i;
                          return null === (i = e.channel) || void 0 === i
                            ? void 0
                            : i.guestStarSessionCall;
                        },
                        function () {
                          return null;
                        }
                      );
                    default:
                      return i;
                  }
                },
              }),
              {
                sessionID:
                  null ===
                    (c =
                      null === (s = null == m ? void 0 : m.channel) ||
                      void 0 === s
                        ? void 0
                        : s.guestStarSessionCall) || void 0 === c
                    ? void 0
                    : c.id,
                loading: k,
              }
            );
          };
      },
      554983: function (e, i, n) {
        "use strict";
        n.d(i, {
          C: function () {
            return r;
          },
        });
        var a = n(783321),
          t = n(267924),
          d = n(525513),
          l = n.n(d),
          r = function (e) {
            var i,
              n = (0, a.IT)(l(), {
                variables: { login: e || "", lookupType: t.agw.ACTIVE },
                skip: !e || !e.length,
              }).data;
            return {
              userID:
                null === (i = null == n ? void 0 : n.user) || void 0 === i
                  ? void 0
                  : i.id,
            };
          };
      },
    },
  ]);
