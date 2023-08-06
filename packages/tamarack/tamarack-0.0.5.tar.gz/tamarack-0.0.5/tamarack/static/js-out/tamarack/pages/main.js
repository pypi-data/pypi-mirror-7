// Compiled by ClojureScript 0.0-2268
goog.provide('tamarack.pages.main');
goog.require('cljs.core');
goog.require('tamarack.pages.all_apps');
goog.require('tamarack.pages.app_endpoint_overview');
goog.require('tamarack.pages.app_endpoint_overview');
goog.require('tamarack.pages.all_apps');
goog.require('tamarack.state');
goog.require('tamarack.state');
goog.require('tamarack.pages.app_dashboard');
goog.require('om.core');
goog.require('om.core');
goog.require('tamarack.pages.app_dashboard');
tamarack.pages.main.page = (function page(app,owner){if(typeof tamarack.pages.main.t7278 !== 'undefined')
{} else
{
/**
* @constructor
*/
tamarack.pages.main.t7278 = (function (owner,app,page,meta7279){
this.owner = owner;
this.app = app;
this.page = page;
this.meta7279 = meta7279;
this.cljs$lang$protocol_mask$partition1$ = 0;
this.cljs$lang$protocol_mask$partition0$ = 393216;
})
tamarack.pages.main.t7278.cljs$lang$type = true;
tamarack.pages.main.t7278.cljs$lang$ctorStr = "tamarack.pages.main/t7278";
tamarack.pages.main.t7278.cljs$lang$ctorPrWriter = (function (this__4145__auto__,writer__4146__auto__,opt__4147__auto__){return cljs.core._write.call(null,writer__4146__auto__,"tamarack.pages.main/t7278");
});
tamarack.pages.main.t7278.prototype.om$core$IRender$ = true;
tamarack.pages.main.t7278.prototype.om$core$IRender$render$arity$1 = (function (_){var self__ = this;
var ___$1 = this;var pred__7281 = cljs.core._EQ_;var expr__7282 = new cljs.core.Keyword(null,"view","view",1247994814).cljs$core$IFn$_invoke$arity$1(self__.app);if(cljs.core.truth_(pred__7281.call(null,new cljs.core.Keyword(null,"app-endpoint-overview","app-endpoint-overview",486981663),expr__7282)))
{return om.core.build.call(null,tamarack.pages.app_endpoint_overview.page,self__.app);
} else
{if(cljs.core.truth_(pred__7281.call(null,new cljs.core.Keyword(null,"app-dashboard","app-dashboard",-106677937),expr__7282)))
{return om.core.build.call(null,tamarack.pages.app_dashboard.page,self__.app);
} else
{if(cljs.core.truth_(pred__7281.call(null,new cljs.core.Keyword(null,"all-apps","all-apps",1203012863),expr__7282)))
{return om.core.build.call(null,tamarack.pages.all_apps.page,self__.app);
} else
{throw (new Error(("No matching clause: "+cljs.core.str.cljs$core$IFn$_invoke$arity$1(expr__7282))));
}
}
}
});
tamarack.pages.main.t7278.prototype.om$core$IWillMount$ = true;
tamarack.pages.main.t7278.prototype.om$core$IWillMount$will_mount$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return window.setInterval(cljs.core.partial.call(null,tamarack.state.update_timeslice,new cljs.core.Keyword(null,"timeslice","timeslice",446627929).cljs$core$IFn$_invoke$arity$1(self__.app)),(1000));
});
tamarack.pages.main.t7278.prototype.om$core$IDisplayName$ = true;
tamarack.pages.main.t7278.prototype.om$core$IDisplayName$display_name$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return "Main";
});
tamarack.pages.main.t7278.prototype.cljs$core$IMeta$_meta$arity$1 = (function (_7280){var self__ = this;
var _7280__$1 = this;return self__.meta7279;
});
tamarack.pages.main.t7278.prototype.cljs$core$IWithMeta$_with_meta$arity$2 = (function (_7280,meta7279__$1){var self__ = this;
var _7280__$1 = this;return (new tamarack.pages.main.t7278(self__.owner,self__.app,self__.page,meta7279__$1));
});
tamarack.pages.main.__GT_t7278 = (function __GT_t7278(owner__$1,app__$1,page__$1,meta7279){return (new tamarack.pages.main.t7278(owner__$1,app__$1,page__$1,meta7279));
});
}
return (new tamarack.pages.main.t7278(owner,app,page,null));
});

//# sourceMappingURL=main.js.map