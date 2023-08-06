<nav class="top-bar" data-topbar>
    <ul class="title-area">
        <li class="name">
            {% if ref_7 %}
            <h1><a href="#">{{ ref_7.text or "Top Bar" }}</a> </h1>
            {% endif %}
        </li>
    </ul>
    <section class="top-bar-section">
        <ul class="left"> 
           {% if ref_41 %}
               {% for key, value in ref_41.subitems.iteritems() %}
                   <li><a href="{{ value.link|replace('screen','html') or '#' }}">{{ value.text }}</a></li>
               {% endfor %}
           {% endif %}
        </ul>
        <ul class="center">
        <li class="has-form"> <div class="row collapse"> <div class="large-8 small-9 columns"> <input type="text" placeholder="Find Stuff"> </div> <div class="large-4 small-3 columns"> <a href="#" class="alert button expand">Search</a> </div> </div> </li>
        </ul>
        <ul class="right">
            <li class="has-dropdown">
                <a href="#">Right Button Dropdown</a>
                <ul class="dropdown">
                    <li><a href="#">First link in dropdown</a></li>
                </ul>
            </li>
        </ul>
    </section>
</nav>
