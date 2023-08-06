<ul class="button-group round">
    {% if ref_66 %}
        {% for key,value in ref_66.subitems.iteritems() %}
             <li><a href="{{ value.link|replace('screen','html') or '#'}}" class="button small">{{ value.text }}</a></li>
        {% endfor %}
    {% endif %}
</ul>
