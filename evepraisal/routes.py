from . import app, views


# Login stuff
app.route('/login', methods=['GET', 'POST'])(views.login)
app.route('/logout')(views.logout)

# Main site stuff
app.route('/', methods=['GET', 'POST'])(views.index)
app.route('/history')(views.history)
app.route('/options', methods=['GET', 'POST'])(views.options)
app.route('/estimate', methods=['POST'])(views.estimate_cost)
app.route('/estimate/<int:result_id>')(views.display_result)
app.route('/latest/', defaults={'limit': 20})(views.latest)
app.route('/latest/limit/<int:limit>')(views.latest)
app.route('/legal')(views.legal)

# Admin-related stuff
app.route('/showoid')(views.show_oid)
app.route('/admin/users')(views.user_admins)
app.route('/admin/users/<int:aid>/remove')(views.remove_admin)
app.route('/admin/users/add', methods=['POST'])(views.add_admin)

app.route('/admin/pricemod')(views.modifiers)
app.route('/admin/pricemod/add', methods=['POST'])(views.add_mod)
app.route('/admin/pricemod/<int:tid>/remove')(views.remove_mod)

# Static Stuff (should really be served from a legit file server)
app.route('/robots.txt')(views.static_from_root)
app.route('/favicon.ico')(views.static_from_root)
