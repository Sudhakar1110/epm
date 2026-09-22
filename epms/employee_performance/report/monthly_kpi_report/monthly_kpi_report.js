function epms_badge(v){if(!v)return'';var s=String(v).toLowerCase(),c='epms-badge-info';if(['on track','excellent','very good','completed','a+','a','b+','b','gold','silver'].indexOf(s)>-1)c='epms-badge-success';else if(['needs attention','good','average','in progress','c','d'].indexOf(s)>-1)c='epms-badge-warning';else if(['at risk','needs improvement','blocked','f','fail'].indexOf(s)>-1)c='epms-badge-danger';else if(['pending'].indexOf(s)>-1)c='epms-badge-muted';return'<span class="epms-badge '+c+'">'+v+'</span>';}
function epms_progress(val){if(val===null||val===undefined||val==='')return'';var pct=parseFloat(String(val).replace('%',''))||0,c='blue';if(pct>=80)c='green';else if(pct>=60)c='yellow';else c='red';return'<div class="epms-progress"><div class="epms-progress-track"><div class="epms-progress-fill '+c+'" style="width:'+Math.min(pct,100)+'%"></div></div><span class="epms-progress-label">'+pct.toFixed(1)+'%</span></div>';}
function epms_fmt(spec){setTimeout(function(){var t=document.querySelector('.page-wrapper table');if(!t)return;var hs=[];t.querySelectorAll('thead th').forEach(function(th){hs.push(th.textContent.trim().toLowerCase());});t.querySelectorAll('tbody tr').forEach(function(r){var cs=r.querySelectorAll('td');hs.forEach(function(h,i){if(spec[h]&&cs[i])cs[i].innerHTML=spec[h](cs[i].textContent.trim());});});},1500);}

frappe.query_reports['Monthly KPI Report']={
    filters:[
        {fieldname:'month',fieldtype:'Select',label:__('Month'),options:'1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12',default:new Date().getMonth()+1,reqd:1},
        {fieldname:'year',fieldtype:'Int',label:__('Year'),default:new Date().getFullYear(),reqd:1}
    ],
    onload:function(r){epms_fmt({'achievement %':epms_progress,'status':epms_badge});}
};
