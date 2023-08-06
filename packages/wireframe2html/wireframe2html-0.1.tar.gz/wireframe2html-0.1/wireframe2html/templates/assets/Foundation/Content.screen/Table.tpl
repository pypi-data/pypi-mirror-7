<table >
    <thead>
        <tr> 
            {% for header in ref_34.text | get_table_header %}
            <th style="padding: 0.3rem 0.625rem;">{{ header|replace('*','') }}</th>
            {% endfor %}
        </tr> 
    </thead> 
    <tbody> 
       {% for ligne in ref_34.text | get_table_lignes %}
        <tr> 
           {% for value in ligne | get_table_ligne_value %}
                <td style="padding: 0.3rem 0.625rem;">{{ value }}</td> 
           {% endfor %}
        </tr> 
        {% endfor %}
    </tbody> 
</table>
