
/* /web/static/src/legacy/js/public/lazyloader.js defined in bundle 'web.assets_frontend_minimal' */
odoo.define('web.public.lazyloader',function(require){'use strict';var blockEvents=['submit','click'];var blockFunction=function(ev){ev.preventDefault();ev.stopImmediatePropagation();};var waitingLazy=false;function waitLazy(){if(waitingLazy){return;}
waitingLazy=true;var lazyEls=document.querySelectorAll('.o_wait_lazy_js');for(var i=0;i<lazyEls.length;i++){var element=lazyEls[i];blockEvents.forEach(function(evType){element.addEventListener(evType,blockFunction);});}}
function stopWaitingLazy(){if(!waitingLazy){return;}
waitingLazy=false;var lazyEls=document.querySelectorAll('.o_wait_lazy_js');for(var i=0;i<lazyEls.length;i++){var element=lazyEls[i];blockEvents.forEach(function(evType){element.removeEventListener(evType,blockFunction);});element.classList.remove('o_wait_lazy_js');}}
if(document.readyState!=='loading'){waitLazy();}else{document.addEventListener('DOMContentLoaded',function(){waitLazy();});}
var doResolve=null;var _allScriptsLoaded=new Promise(function(resolve){if(doResolve){resolve();}else{doResolve=resolve;}}).then(function(){stopWaitingLazy();});if(document.readyState==='complete'){setTimeout(_loadScripts,0);}else{window.addEventListener('load',function(){setTimeout(_loadScripts,0);});}
function _loadScripts(scripts,index){if(scripts===undefined){scripts=document.querySelectorAll('script[data-src]');}
if(index===undefined){index=0;}
if(index>=scripts.length){if(typeof doResolve==='function'){doResolve();}else{doResolve=true;}
return;}
var script=scripts[index];script.addEventListener('load',_loadScripts.bind(this,scripts,index+1));script.src=script.dataset.src;script.removeAttribute('data-src');}
return{loadScripts:_loadScripts,allScriptsLoaded:_allScriptsLoaded,};});;

/* /web_editor/static/src/js/frontend/loader_loading.js defined in bundle 'web.assets_frontend_minimal' */
(function(){'use strict';document.addEventListener('DOMContentLoaded',()=>{var textareaEls=document.querySelectorAll('textarea.o_wysiwyg_loader');for(var i=0;i<textareaEls.length;i++){var textarea=textareaEls[i];var wrapper=document.createElement('div');wrapper.classList.add('position-relative','o_wysiwyg_textarea_wrapper');var loadingElement=document.createElement('div');loadingElement.classList.add('o_wysiwyg_loading');var loadingIcon=document.createElement('i');loadingIcon.classList.add('text-600','text-center','fa','fa-circle-o-notch','fa-spin','fa-2x');loadingElement.appendChild(loadingIcon);wrapper.appendChild(loadingElement);textarea.parentNode.insertBefore(wrapper,textarea);wrapper.insertBefore(textarea,loadingElement);}});})();;

/* /website/static/src/js/content/inject_dom.js defined in bundle 'web.assets_frontend_minimal' */
odoo.define('@website/js/content/inject_dom',async function(require){'use strict';let __exports={};const{get_cookie}=require('web.utils.cookies');const{session}=require('@web/session');document.addEventListener('DOMContentLoaded',()=>{const htmlEl=document.documentElement;const cookieNamesToDataNames={'utm_source':'utmSource','utm_medium':'utmMedium','utm_campaign':'utmCampaign',};for(const[name,dsName]of Object.entries(cookieNamesToDataNames)){const cookie=get_cookie(`odoo_${name}`);if(cookie){htmlEl.dataset[dsName]=cookie.replace(/(^["']|["']$)/g,'');}}
const country=session.geoip_country_code;if(country){htmlEl.dataset.country=country;}
htmlEl.dataset.logged=!session.is_website_user;const styleEl=document.createElement('style');styleEl.id="conditional_visibility";document.head.appendChild(styleEl);const conditionalEls=document.querySelectorAll('[data-visibility="conditional"]');for(const conditionalEl of conditionalEls){const selectors=conditionalEl.dataset.visibilitySelectors;styleEl.sheet.insertRule(`${selectors} { display: none !important; }`);}
for(const conditionalEl of conditionalEls){conditionalEl.classList.remove('o_conditional_hidden');}});return __exports;});;

/* /website/static/src/js/content/auto_hide_menu.js defined in bundle 'web.assets_frontend_minimal' */
odoo.define('@website/js/content/auto_hide_menu',async function(require){'use strict';let __exports={};const{initAutoMoreMenu}=require('@web/legacy/js/core/menu');document.addEventListener('DOMContentLoaded',async()=>{const header=document.querySelector('header#top');if(header){const topMenu=header.querySelector('#top_menu');if(header.classList.contains('o_no_autohide_menu')){topMenu.classList.remove('o_menu_loading');return;}
const unfoldable='.divider, .divider ~ li, .o_no_autohide_item, .js_language_selector';const excludedImagesSelector='.o_mega_menu, .o_offcanvas_logo_container, .o_lang_flag';const excludedImages=[...header.querySelectorAll(excludedImagesSelector)];const images=[...header.querySelectorAll('img')].filter((img)=>{excludedImages.forEach(node=>{if(node.contains(img)){return false;}});return img.matches&&!img.matches(excludedImagesSelector);});initAutoMoreMenu(topMenu,{unfoldable:unfoldable,images:images,loadingStyleClasses:['o_menu_loading']});}});return __exports;});