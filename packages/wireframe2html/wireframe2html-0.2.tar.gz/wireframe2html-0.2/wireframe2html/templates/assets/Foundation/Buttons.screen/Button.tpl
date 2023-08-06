<a href="{% if ref_20 %}{{ ref_20.link|replace('screen','html') or '#' }}{% endif %}" class="button radius" style="width:auto; height:auto;font-size:14px">
{% if ref_20 %}
{{ ref_20.text or 'Default Button' }}
{% else %}
Default
{% endif %}
</a>
