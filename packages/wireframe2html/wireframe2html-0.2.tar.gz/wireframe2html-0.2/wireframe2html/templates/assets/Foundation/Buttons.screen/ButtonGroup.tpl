<ul class="button-group round">
    {% if ref_68 %}
        {% for key,value in ref_68.subitems.iteritems() %}
             <li style="padding: Opx"><a href="{{ value.link|replace('screen','html') or '#'}}" class="button" style="front-size:12px">{{ value.text }}</a></li>
        {% endfor %}
    {% endif %}
</ul>
