<ul class="button-group round">
    {% if ref_70 %}
        {% for key,value in ref_70.subitems.iteritems() %}
             <li><a href="{{ value.link|replace('screen','html') or '#'}}" class="button large">{{ value.text }}</a></li>
        {% endfor %}
    {% endif %}
</ul>
