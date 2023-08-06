// Compiled by ClojureScript 0.0-2234
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
tamarack.pages.main.page = (function page(app,owner){if(typeof tamarack.pages.main.t7229 !== 'undefined')
{} else
{
/**
* @constructor
*/
tamarack.pages.main.t7229 = (function (owner,app,page,meta7230){
this.owner = owner;
this.app = app;
this.page = page;
this.meta7230 = meta7230;
this.cljs$lang$protocol_mask$partition1$ = 0;
this.cljs$lang$protocol_mask$partition0$ = 393216;
})
tamarack.pages.main.t7229.cljs$lang$type = true;
tamarack.pages.main.t7229.cljs$lang$ctorStr = "tamarack.pages.main/t7229";
tamarack.pages.main.t7229.cljs$lang$ctorPrWriter = (function (this__4140__auto__,writer__4141__auto__,opt__4142__auto__){return cljs.core._write.call(null,writer__4141__auto__,"tamarack.pages.main/t7229");
});
tamarack.pages.main.t7229.prototype.om$core$IRender$ = true;
tamarack.pages.main.t7229.prototype.om$core$IRender$render$arity$1 = (function (_){var self__ = this;
var ___$1 = this;var pred__7232 = cljs.core._EQ_;var expr__7233 = new cljs.core.Keyword(null,"view","view",1017523735).cljs$core$IFn$_invoke$arity$1(self__.app);if(cljs.core.truth_(pred__7232.call(null,new cljs.core.Keyword(null,"app-endpoint-overview","app-endpoint-overview",4188672375),expr__7233)))
{return om.core.build.call(null,tamarack.pages.app_endpoint_overview.page,self__.app);
} else
{if(cljs.core.truth_(pred__7232.call(null,new cljs.core.Keyword(null,"app-dashboard","app-dashboard",3494823258),expr__7233)))
{return om.core.build.call(null,tamarack.pages.app_dashboard.page,self__.app);
} else
{if(cljs.core.truth_(pred__7232.call(null,new cljs.core.Keyword(null,"all-apps","all-apps",2765439632),expr__7233)))
{return om.core.build.call(null,tamarack.pages.all_apps.page,self__.app);
} else
{throw (new Error(("No matching clause: "+cljs.core.str.cljs$core$IFn$_invoke$arity$1(expr__7233))));
}
}
}
});
tamarack.pages.main.t7229.prototype.om$core$IWillMount$ = true;
tamarack.pages.main.t7229.prototype.om$core$IWillMount$will_mount$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return window.setInterval(cljs.core.partial.call(null,tamarack.state.update_timeslice,new cljs.core.Keyword(null,"timeslice","timeslice",1068799575).cljs$core$IFn$_invoke$arity$1(self__.app)),1000);
});
tamarack.pages.main.t7229.prototype.om$core$IDisplayName$ = true;
tamarack.pages.main.t7229.prototype.om$core$IDisplayName$display_name$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return "Main";
});
tamarack.pages.main.t7229.prototype.cljs$core$IMeta$_meta$arity$1 = (function (_7231){var self__ = this;
var _7231__$1 = this;return self__.meta7230;
});
tamarack.pages.main.t7229.prototype.cljs$core$IWithMeta$_with_meta$arity$2 = (function (_7231,meta7230__$1){var self__ = this;
var _7231__$1 = this;return (new tamarack.pages.main.t7229(self__.owner,self__.app,self__.page,meta7230__$1));
});
tamarack.pages.main.__GT_t7229 = (function __GT_t7229(owner__$1,app__$1,page__$1,meta7230){return (new tamarack.pages.main.t7229(owner__$1,app__$1,page__$1,meta7230));
});
}
return (new tamarack.pages.main.t7229(owner,app,page,null));
});

//# sourceMappingURL=main.js.map