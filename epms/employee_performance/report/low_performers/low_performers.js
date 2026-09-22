function epms_badge(v){if(!v)return'';var s=String(v).toLowerCase(),c='epms-badge-info';if(['on track','excellent','very good','completed','a+','a','b+','b','gold','silver'].indexOf(s)>-1)c='epms-badge-success';else if(['needs attention','good','average','in progress','c','d'].indexOf(s)>-1)c='epms-badge-warning';else if(['at risk','needs improvement','blocked','f','fail'].indexOf(s)>-1)c='epms-badge-danger';else if(['pending'].indexOf(s)>-1)c='epms-badge-muted';return'<span class="epms-badge '+c+'">'+v+'</span>';}
function epms_score(v){if(v===null||v===undefined||v==='')return'0';var n=parseFloat(v)||0,c='epms-badge-success';if(n<60)c='epms-badge-danger';else if(n<80)c='epms-badge-warning';return'<span class="epms-badge '+c+'">'+n.toFixed(1)+'</span>';}
function epms_fmt(spec){setTimeout(function(){var t=document.querySelector('.page-wrapper table');if(!t)return;var hs=[];t.querySelectorAll('thead th').forEach(function(th){hs.push(th.textContent.trim().toLowerCase());});t.querySelectorAll('tbody tr').forEach(function(r){var cs=r.querySelectorAll('td');hs.forEach(function(h,i){if(spec[h]&&cs[i])cs[i].innerHTML=spec[h](cs[i].textContent.trim());});});},1500);}

frappe.query_reports['Low Performers']={
    filters:[
        {fieldname:'month',fieldtype:'Select',label:__('Month'),options:'1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12',default:new Date().getMonth()+1,reqd:1},
        {fieldname:'year',fieldtype:'Int',label:__('Year'),default:new Date().getFullYear(),reqd:1},
        {fieldname:'team',fieldtype:'Link',label:__('Team'),options:'Team'},
        {fieldname:'threshold',fieldtype:'Int',label:__('Score Threshold'),default:60,description:__('Show employees with score below this value')}
    ],
    onload:function(r){epms_fmt({'overall score':epms_score,'grade':epms_badge,'status':epms_badge});}
};
