// Compiled by ClojureScript 0.0-2268
goog.provide('tamarack.state');
goog.require('cljs.core');
goog.require('tamarack.xhr');
goog.require('tamarack.xhr');
goog.require('tamarack.util');
goog.require('tamarack.util');
goog.require('clojure.string');
goog.require('clojure.string');
goog.require('om.core');
goog.require('om.core');
tamarack.state.app_state = cljs.core.atom.call(null,null);
tamarack.state.default_tracking_now_window_size = ((60) * (30));
tamarack.state.timeslice_ending_now = (function timeslice_ending_now(window_size){var now = tamarack.util.subtract_seconds.call(null,(new Date()),((2) * (60)));return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [tamarack.util.trunc_to_minute.call(null,tamarack.util.subtract_seconds.call(null,now,window_size)),tamarack.util.trunc_to_minute.call(null,now)], null);
});
tamarack.state.update_timeslice = (function update_timeslice(app){if(cljs.core.truth_(new cljs.core.Keyword(null,"tracking-now","tracking-now",-2134671757).cljs$core$IFn$_invoke$arity$1(cljs.core.deref.call(null,app))))
{return om.core.update_BANG_.call(null,app,new cljs.core.Keyword(null,"window","window",724519534),tamarack.state.timeslice_ending_now.call(null,new cljs.core.Keyword(null,"window-size","window-size",923834855).cljs$core$IFn$_invoke$arity$1(cljs.core.deref.call(null,app))));
} else
{return null;
}
});
tamarack.state.track_now_BANG_ = (function track_now_BANG_(app,window_size){om.core.update_BANG_.call(null,app,new cljs.core.Keyword(null,"window-size","window-size",923834855),window_size);
om.core.update_BANG_.call(null,app,new cljs.core.Keyword(null,"tracking-now","tracking-now",-2134671757),true);
return tamarack.state.update_timeslice.call(null,app);
});
tamarack.state.merge_state_BANG_ = (function merge_state_BANG_(state){var new_app = new cljs.core.Keyword(null,"current-app","current-app",1533042174).cljs$core$IFn$_invoke$arity$1(state);var known_apps = new cljs.core.Keyword(null,"all-apps","all-apps",1203012863).cljs$core$IFn$_invoke$arity$1(cljs.core.deref.call(null,tamarack.state.app_state));var known_app = (cljs.core.truth_((function (){var and__3566__auto__ = known_apps;if(cljs.core.truth_(and__3566__auto__))
{return new_app;
} else
{return and__3566__auto__;
}
})())?new cljs.core.Keyword(null,"all-apps","all-apps",1203012863).cljs$core$IFn$_invoke$arity$1(cljs.core.deref.call(null,tamarack.state.app_state)).call(null,new cljs.core.Keyword(null,"name","name",1843675177).cljs$core$IFn$_invoke$arity$1(new_app)):new_app);var state_SINGLEQUOTE_ = cljs.core.assoc.call(null,state,new cljs.core.Keyword(null,"current-app","current-app",1533042174),known_app);if(cljs.core.truth_((function (){var and__3566__auto__ = new_app;if(cljs.core.truth_(and__3566__auto__))
{return (new cljs.core.Keyword(null,"display-name","display-name",694513143).cljs$core$IFn$_invoke$arity$1(known_app) == null);
} else
{return and__3566__auto__;
}
})()))
{var url_7300 = clojure.string.join.call(null,"/",new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, ["/explorer-api/v1/applications",new cljs.core.Keyword(null,"name","name",1843675177).cljs$core$IFn$_invoke$arity$1(known_app)], null));tamarack.xhr.send_edn.call(null,new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"method","method",55703592),new cljs.core.Keyword(null,"get","get",1683182755),new cljs.core.Keyword(null,"url","url",276297046),url_7300,new cljs.core.Keyword(null,"on-complete","on-complete",-1531183971),((function (url_7300,new_app,known_apps,known_app,state_SINGLEQUOTE_){
return (function (res){return cljs.core.swap_BANG_.call(null,tamarack.state.app_state,cljs.core.merge,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"current-app","current-app",1533042174),res], null));
});})(url_7300,new_app,known_apps,known_app,state_SINGLEQUOTE_))
], null));
} else
{}
return cljs.core.swap_BANG_.call(null,tamarack.state.app_state,cljs.core.merge,state_SINGLEQUOTE_);
});
tamarack.state.init_state = (function init_state(){var window = tamarack.state.timeslice_ending_now.call(null,tamarack.state.default_tracking_now_window_size);var window_size = tamarack.state.default_tracking_now_window_size;return cljs.core.reset_BANG_.call(null,tamarack.state.app_state,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"timeslice","timeslice",446627929),new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"window","window",724519534),window,new cljs.core.Keyword(null,"window-size","window-size",923834855),window_size,new cljs.core.Keyword(null,"tracking-now","tracking-now",-2134671757),true], null)], null));
});

//# sourceMappingURL=state.js.map