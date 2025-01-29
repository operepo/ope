namespace :ope do
  desc "Deal with OPE specific startup and configuration tasks"
  
  # Make startup the default task
  task :default => ["startup"]
  
  task :startup => [:environment, "startup_init_env", "startup_db_init", "startup_db_migrate", "db:reset_encryption_key_hash", 'ope:init_auditing', 'ope:set_sequence_range', 'ope:enable_auditing', "startup_apply_admin_settings", "ensure_jwk_key"] do
  
   
    # Startup itmes are set as pre-requisites so when we get here, it should be done
    puts "====== OPE STARTUP COMPLETE ======"
    
  end

  task :startup_init_env => [:environment] do
    puts "====== OPE STARTUP_INIT BEGIN ======"
    # Make sure we have info in our environment
    if (ENV["CANVAS_LMS_ACCOUNT_NAME"] || "").empty?
        puts "==== ERR - CANVAS_LMS_ACCOUNT_NAME empty ===="
        ENV["CANVAS_LMS_ACCOUNT_NAME"] = "Open Prison Education"
    end
    # Chomp off quotes - old installs ended up with quotes in the name
    ENV["CANVAS_LMS_ACCOUNT_NAME"] =  ENV["CANVAS_LMS_ACCOUNT_NAME"].tr('"', '')

    if (ENV["CANVAS_LMS_ADMIN_EMAIL"] || "").empty?
        puts "==== ERR - CANVAS_LMS_ADMIN_EMAIL empty ===="
        ENV["CANVAS_LMS_ADMIN_EMAIL"] = "admin@ed"
    end

    if (ENV["CANVAS_LMS_ADMIN_PASSWORD"] || "").empty?
        puts "==== ERR - CANVAS_LMS_ADMIN_PASSWORD empty ===="
        ENV["CANVAS_LMS_ADMIN_PASSWORD"] = "changeme331"
    end
    
    if (ENV["CANVAS_LMS_STATS_COLLECTION"] || "").empty?
        ENV["CANVAS_LMS_STATS_COLLECTION"] = "opt_out"
    end

    if (ENV["TIME_ZONE"] || "").empty?
        ENV["TIME_ZONE"] = "Pacific Time (US & Canada)"
    end

    if (ENV["CANVAS_LOGIN_PROMPT"] || "").empty?
        ENV["CANVAS_LOGIN_PROMPT"] = "Student ID (default is s + DOC number - s113412)"
    end

    if (ENV["CANVAS_DEFAULT_DOMAIN"] || "").empty?
        ENV["CANVAS_DEFAULT_DOMAIN"] = "canvas.ed"
    end
    puts "====== OPE STARTUP_INIT END ======"
  end
  
  
  task :startup_db_init => [:environment, "startup_init_env"] do
    puts "====== OPE STARTUP_DB_INIT BEGIN ======"
    # See if file .db_init_done exists - if it doesn't, run db:initial_setup
    db_init_done_file = "/usr/src/app/tmp/db_init_done"
    if File.file?(db_init_done_file) == true
        puts "==== DB Init done - skipping ===="
    else
        puts "==== Canvas DB does NOT exist, creating ===="
        Rake::Task['db:initial_setup'].invoke
        # Save the file so we show db init finished
        begin
            File.open(db_init_done_file, 'w') do |f|
                f.puts "DB Init Run"
            end
        rescue
            puts "=== ERROR - writing #{db_init_done_file}"
        end
        puts "==== END Canvas DB does NOT exist, creating ===="
    end

    puts "====== OPE STARTUP_DB_INIT END ======"
  end
  
  task :fix_null_root_account_ids => [:environment] do
    # After some migrate/predeploy some root_account_id fields end up null, fix them
    
    # Fix roles table
    Role.where(:root_account_id => nil).update_all(:root_account_id => 1)
    #Role.where(:root_account_id => nil).delete_all
    #RoleOverride.where(:root_account_id => nil).delete_all
    RoleOverride.where(:root_account_id => nil).update_all(:root_account_id => 1)
    #RoleOverride.where(:root_account_id => 0).delete_all
    #.update_all(:root_account_id => 1)
    
    # Clear redis cache
    GuardRail.activate!(:deploy)
    Canvas.redis.flushall
    GuardRail.activate!(:primary)
  end
  
  # task :startup_db_migrate => [:environment, "startup_db_init"] do
  task :startup_db_migrate => [:environment, "startup_db_init", "db:migrate:predeploy", "fix_null_root_account_ids"  ] do
    puts "====== OPE STARTUP_DB_MIGRATE BEGIN ======"
    # ==== Init DB if not already done
    db_changed = 0
    
    # ==== Run db migrate
    # Get the number of schema migrations so we can see if db:migrate changes anything
    pre_migrations = 0
    post_migrations = 0
    
    sql_row = ActiveRecord::Base.connection.exec_query("select count(*) as cnt from schema_migrations")
    sql_row.each do |row|
        pre_migrations = row["cnt"].to_i
    end
		
    puts "==== Running db:migrate ===="
    Rake::Task['db:migrate'].invoke
    puts "==== END Running db:migrate ===="
    
    # Get the number after migrations
    sql_row = ActiveRecord::Base.connection.exec_query("select count(*) as cnt from schema_migrations")
    sql_row.each do |row|
        post_migrations = row["cnt"].to_i
    end

    if (pre_migrations != post_migrations)
        db_changed = 1
    end

    # Make sure that the assets are properly compiled (run this each time as a migrate may require a recompile)
    if (db_changed == 1)
        puts "==== DB Migrations detected ===="
        # Rake::Task['canvas:compile_assets'].invoke
        # NOTE: Shouldn't need recompile - should have been done in docker build, just do brand_configs
        puts "====> brand_configs:generate_and_upload_all..."
        Rake::Task['brand_configs:generate_and_upload_all'].invoke
        puts "====> END brand_configs:generate_and_upload_all..."
    else
        puts "====> No DB migrations detected"
    end
    puts "====== OPE STARTUP_DB_MIGRATE END ======"
  end
  
  task :startup_apply_admin_settings => [:environment, "startup_db_migrate"] do
    puts "====== OPE STARTUP_APPLY_ADMIN_SETTINGS BEGIN ======"
    
    # Make sure admin account exists - should always be id 1
    #puts "==== Ensuring Admin Account Exists ===="

    #account = Account.find_by(id: 1)
    #if (account)
    #    puts "==== Admin account exists ===="
    #else
    #    puts "==== Admin account not found - loading initial data ===="
    #    #Rake::Task['db:initial_setup'].invoke
    #    Rake::Task['db:load_initial_data'].invoke
    #    puts "==== END Admin account not found - loading initial data ===="
    #end

    #account = Account.find_by(id: 1)
    #if (account)
    #    puts "==== Admin account exists ===="
    #else
    #    puts "==== Admin account not found - creating ===="
    #    ActiveRecord::Base.transaction do
    #      begin
    #          # Create the user
    #          account = Account.create!(
    #              id: 1,
    #              name: acct_name,
    #          )
    #          user = User.create!(
    #              name: acct_name,
    #              short_name: acct_name,
    #              sortable_name: acct_name
    #          )
    #          # Create the pseudonym for login
    #          pseudonym = Pseudonym.create!(
    #              :account => account,
    #              :unique_id => acct_email,
    #              :user => user
    #          )
    #          pseudonym.password = pseudonym.password_confirmation = acct_pw
    #          pseudonym.save!
    #
    #          puts "==== Admin Account Created - login with #{acct_email} ===="
    #      rescue => e
    #          puts "====> ERROR Creating Admin Account ===="
    #          puts e
    #          raise ActiveRecord::Rollback
    #      end
    #    end
    #end
    #puts "==== END Ensuring Admin Account Exists ===="
    
    # Early installs had " characters around the account name. Change that so they are removed.
    tmp = Account.where(name: "\"" + ENV["CANVAS_LMS_ACCOUNT_NAME"] + "\"").first
    if (tmp)
        tmp.name = ENV["CANVAS_LMS_ACCOUNT_NAME"]
        tmp.save
    end

    # Set canvas options
    admin_account = Account.where(name: ENV["CANVAS_LMS_ACCOUNT_NAME"] ).first
    site_admin_account = Account.where(name: "Site Admin" ).first
    if (admin_account && site_admin_account)
        puts "==== Setting Canvas Config Settings ===="

        # Tell canvas not to send reports home
        Setting.set("usage_statistics_collection", "opt_out")
        # Change request throttle so LMS doesn't get blocked during high traffic
        Setting.set("request_throttle.hwm", '100000')
        #Setting.set("request_throttle.enabled", false)
        Setting.set("request_throttle.maximum", '100000')
        Setting.set("request_throttle.outflow", '50')
        Setting.set("login_attempts_per_ip", '100')
        Setting.set("api_max_per_page", '100')

        admin_account.default_time_zone = ENV["TIME_ZONE"]  # "Pacific Time (US & Canada)"
        site_admin_account.default_time_zone = ENV["TIME_ZONE"]  # "Pacific Time (US & Canada)"
        admin_account.allow_sis_import = true
        site_admin_account.allow_sis_import = true
        
        # Feature.definitions['common_cartridge_page_conversion']
        # admin_account.feature_disabled(:common_cartridge_page_conversion)
        # admin_account.feature_disabled(:rich_content_service)
        # admin_account.disable_feature!(:rich_content_service_high_risk)
        # rails console
        # a = Account.site_admin
        # a.enable_feature!(:...) or disable_feature! or allow_feature!

        # Disable web services
        admin_account.disable_service("google_docs_previews")
        admin_account.disable_service("skype")
        admin_account.disable_service("delicious")
        site_admin_account.disable_service("google_docs_previews")
        site_admin_account.disable_service("skype")
        site_admin_account.disable_service("delicious")

        # Enable the mathman plugin
        mathman = Canvas::Plugin.find(:mathman)
        #if mathman.has_settings_partial?
        #    # Need to setup initial settings?
        #end
        # Need its settings
        mm_settings = PluginSetting.find_by_name(mathman.id)
        # Do this to load defaults if settings are empty
        mm_settings ||= PluginSetting.new(:name => mathman.id, :settings => mathman.default_settings) { |ps| ps.disabled = false }
        mm_settings.disabled = false
        mm_settings.posted_settings = {"use_for_svg"=>"1", "use_for_mml"=>"1"}        
        mm_settings.save

        # Allow admin account to change / set passwords - needed by SMC
        site_admin_account.settings[:admins_can_change_passwords] = admin_account.settings[:admins_can_change_passwords] = true
        site_admin_account.settings[:edit_institution_email] = admin_account.settings[:edit_institution_email] = false
        site_admin_account.settings[:admins_can_view_notifications] = admin_account.settings[:admins_can_view_notifications] = true
        site_admin_account.settings[:allow_invitation_previews] = admin_account.settings[:allow_invitation_previews] = false
        site_admin_account.settings[:allow_sending_scores_in_emails] = admin_account.settings[:allow_sending_scores_in_emails] = false
        site_admin_account.settings[:author_email_in_notifications] = admin_account.settings[:author_email_in_notifications] = false
        site_admin_account.settings[:enable_alerts] = admin_account.settings[:enable_alerts] = false
        site_admin_account.settings[:enable_portfolios] = admin_account.settings[:enable_portfolios] = false
        site_admin_account.settings[:enable_eportfolios] = admin_account.settings[:enable_eportfolios] = false
        site_admin_account.settings[:enable_offline_web_export] = admin_account.settings[:enable_offline_web_export] = false
        site_admin_account.settings[:enable_profiles] = admin_account.settings[:enable_profiles] = false
        site_admin_account.settings[:enable_gravatar] = admin_account.settings[:enable_gravatar] = false
        site_admin_account.settings[:enable_turnitin] = admin_account.settings[:enable_turnitin] = false
        site_admin_account.settings[:global_includes] = admin_account.settings[:global_includes] = true
        site_admin_account.settings[:include_students_in_global_survey] = admin_account.settings[:include_students_in_global_survey] = false
        site_admin_account.settings[:lock_all_announcements] = admin_account.settings[:lock_all_announcements] = true
        site_admin_account.settings[:mfa_settings] = admin_account.settings[:mfa_settings] = "disabled"
        site_admin_account.settings[:no_enrollments_can_create_courses] = admin_account.settings[:no_enrollments_can_create_courses] = false
        site_admin_account.settings[:open_registration] = admin_account.settings[:open_registration] = false
        site_admin_account.settings[:prevent_course_renaming_by_teachers] = admin_account.settings[:prevent_course_renaming_by_teachers] = false
        site_admin_account.settings[:restrict_quiz_questions] = admin_account.settings[:restrict_quiz_questions] = true
        site_admin_account.settings[:restrict_student_future_listing] = admin_account.settings[:restrict_student_future_listing] = false
        site_admin_account.settings[:restrict_student_future_view] = admin_account.settings[:restrict_student_future_view] = true
        site_admin_account.settings[:restrict_student_past_view] = admin_account.settings[:restrict_student_past_view] = true
        site_admin_account.settings[:show_scheduler] = admin_account.settings[:show_scheduler] = false
        site_admin_account.settings[:students_can_create_courses] = admin_account.settings[:students_can_create_courses] = false
        site_admin_account.settings[:sub_accunt_includes] = admin_account.settings[:sub_accunt_includes] = false
        site_admin_account.settings[:teachers_can_create_courses] = admin_account.settings[:teachers_can_create_courses] = false
        site_admin_account.settings[:users_can_edit_name] = admin_account.settings[:users_can_edit_name] = false
        site_admin_account.settings[:login_handle_name] = admin_account.settings[:login_handle_name] = ENV["CANVAS_LOGIN_PROMPT"]
        # "Student ID (default is s + DOC number - s113412)"
        site_admin_account.settings[:self_enrollment] = admin_account.settings[:self_enrollment] = "Never"


        # Default storage quotas
        admin_account.default_storage_quota_mb=5000
        admin_account.default_user_storage_quota_mb=1
        admin_account.default_group_storage_quota_mb=1
        site_admin_account.default_storage_quota_mb=5000
        site_admin_account.default_user_storage_quota_mb=1
        site_admin_account.default_group_storage_quota_mb=1
        
        # Lock down permissions
        puts "^^^ Getting role: root_id #{admin_account.id} ^^^"
        student_role = Role.get_built_in_role("StudentEnrollment", root_account_id: admin_account.id)
        ta_role = Role.get_built_in_role("TaEnrollment", root_account_id: admin_account.id)
        puts "^ Got Roles: #{student_role} / #{ta_role} ^"

        # Calendar access
        admin_account.role_overrides.where(role: student_role, permission: :manage_calendar).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :manage_calendar)
        admin_account.role_overrides.where(role: ta_role, permission: :manage_calendar).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :manage_calendar)

        # Add / Remove teachers
        admin_account.role_overrides.where(role: student_role, permission: :manage_admins).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :manage_admins)
        admin_account.role_overrides.where(role: ta_role, permission: :manage_admins).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :manage_admins)

        # Add / Remove students
        admin_account.role_overrides.where(role: student_role, permission: :manage_students).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :manage_students)
        admin_account.role_overrides.where(role: ta_role, permission: :manage_students).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :manage_students)

        # Change course state
        admin_account.role_overrides.where(role: student_role, permission: :change_course_state).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :change_course_state)
        admin_account.role_overrides.where(role: ta_role, permission: :change_course_state).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :change_course_state)

        # Manage Ruberics
        admin_account.role_overrides.where(role: student_role, permission: :manage_rubrics).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :manage_rubrics)
        admin_account.role_overrides.where(role: ta_role, permission: :manage_rubrics).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :manage_rubrics)

        # Manage student collaborations
        admin_account.role_overrides.where(role: student_role, permission: :create_collaborations).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :create_collaborations)
        admin_account.role_overrides.where(role: ta_role, permission: :create_collaborations).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :create_collaborations)
        
        # Mange web conferences
        admin_account.role_overrides.where(role: student_role, permission: :create_conferences).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :create_conferences)
        admin_account.role_overrides.where(role: ta_role, permission: :create_conferences).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :create_conferences)

        # Edit Grades
        admin_account.role_overrides.where(role: student_role, permission: :manage_grades).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :manage_grades)
        admin_account.role_overrides.where(role: ta_role, permission: :manage_grades).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :manage_grades)

        # Manage LTI
        admin_account.role_overrides.where(role: student_role, permission: :lti_add_edit).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :lti_add_edit)
        admin_account.role_overrides.where(role: ta_role, permission: :lti_add_edit).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :lti_add_edit)

        # Manages Assignments and Quizzes
        admin_account.role_overrides.where(role: student_role, permission: :manage_assignments).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :manage_assignments)
        admin_account.role_overrides.where(role: ta_role, permission: :manage_assignments).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: true, permission: :manage_assignments)

        # Manage course files
        admin_account.role_overrides.where(role: student_role, permission: :manage_files).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :manage_files)
        admin_account.role_overrides.where(role: ta_role, permission: :manage_files).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: true, permission: :manage_files)

        # Manage Pages
        admin_account.role_overrides.where(role: student_role, permission: :manage_wiki).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :manage_wiki)
        admin_account.role_overrides.where(role: ta_role, permission: :manage_wiki).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: true, permission: :manage_wiki)

        # Manage sections
        admin_account.role_overrides.where(role: student_role, permission: :manage_sections).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :manage_sections)
        admin_account.role_overrides.where(role: ta_role, permission: :manage_sections).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: true, permission: :manage_sections)

        # Manage Groups
        admin_account.role_overrides.where(role: student_role, permission: :manage_groups).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :manage_groups)
        admin_account.role_overrides.where(role: ta_role, permission: :manage_groups).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :manage_groups)

        # Manage Alerts
        admin_account.role_overrides.where(role: student_role, permission: :manage_interaction_alerts).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :manage_interaction_alerts)
        admin_account.role_overrides.where(role: ta_role, permission: :manage_interaction_alerts).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :manage_interaction_alerts)

        # Manage all other course content
        admin_account.role_overrides.where(role: student_role, permission: :manage_content).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :manage_content)
        admin_account.role_overrides.where(role: ta_role, permission: :manage_content).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: true, permission: :manage_content)

        # Mange learning outcomes
        admin_account.role_overrides.where(role: student_role, permission: :manage_outcomes).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :manage_outcomes)
        admin_account.role_overrides.where(role: ta_role, permission: :manage_outcomes).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :manage_outcomes)

        # Moderate Grades
        admin_account.role_overrides.where(role: student_role, permission: :moderate_grades).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :moderate_grades)
        admin_account.role_overrides.where(role: ta_role,  permission: :moderate_grades).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :moderate_grades)

        # Moderate Discussions
        admin_account.role_overrides.where(role: student_role, permission: :moderate_forum).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :moderate_forum)
        admin_account.role_overrides.where(role: ta_role, permission: :moderate_forum).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :moderate_forum)

        # Post to discussions
        admin_account.role_overrides.where(role: student_role, permission: :post_to_forum).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :post_to_forum)
        admin_account.role_overrides.where(role: ta_role, permission: :post_to_forum).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :post_to_forum)

        # Read SIS data
        admin_account.role_overrides.where(role: student_role, permission: :read_sis).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :read_sis)
        admin_account.role_overrides.where(role: ta_role, permission: :read_sis).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :read_sis)

        # See list of users
        admin_account.role_overrides.where(role: student_role, permission: :read_roster).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :read_roster)
        admin_account.role_overrides.where(role: ta_role, permission: :read_roster).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :read_roster)

        # Send messages to individual course memebers
        admin_account.role_overrides.where(role: student_role, permission: :send_messages).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :send_messages)
        admin_account.role_overrides.where(role: ta_role, permission: :send_messages).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :send_messages)

        # Send messages to entire class
        admin_account.role_overrides.where(role: student_role, permission: :send_messages_all).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :send_messages_all)
        admin_account.role_overrides.where(role: ta_role, permission: :send_messages_all).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :send_messages_all)

        # View grades
        admin_account.role_overrides.where(role: student_role, permission: :view_all_grades).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :view_all_grades)
        admin_account.role_overrides.where(role: ta_role, permission: :view_all_grades).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :view_all_grades)

        # View submissions and make comments
        admin_account.role_overrides.where(role: student_role, permission: :comment_on_others_submissions).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :comment_on_others_submissions)
        admin_account.role_overrides.where(role: ta_role, permission: :comment_on_others_submissions).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :comment_on_others_submissions)

        # View and link question banks
        admin_account.role_overrides.where(role: student_role, permission: :read_question_banks).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :read_question_banks)
        admin_account.role_overrides.where(role: ta_role, permission: :read_question_banks).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: true, permission: :read_question_banks)

        # View announcements
        admin_account.role_overrides.where(role: student_role, permission: :read_announcements).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: true, permission: :read_announcements)
        admin_account.role_overrides.where(role: ta_role, permission: :read_announcements).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: true, permission: :read_announcements)

        # View discussions
        admin_account.role_overrides.where(role: student_role, permission: :read_forum).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :read_forum)
        admin_account.role_overrides.where(role: ta_role, permission: :read_forum).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :read_forum)

        # View group pages
        admin_account.role_overrides.where(role: student_role, permission: :view_group_pages).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :view_group_pages)
        admin_account.role_overrides.where(role: ta_role, permission: :view_group_pages).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :view_group_pages)

        # View usage reports
        admin_account.role_overrides.where(role: student_role, permission: :read_reports).destroy_all
        admin_account.role_overrides.create(role: student_role, enabled: false, permission: :read_reports)
        admin_account.role_overrides.where(role: ta_role, permission: :read_reports).destroy_all
        admin_account.role_overrides.create(role: ta_role, enabled: false, permission: :read_reports)



        admin_account.save
        site_admin_account.save
    else
        puts "==== ERROR - Unable to find root account! ===="
    end

    # Reset password for admin user to pw provided in the environment
    puts "==== Resetting admin password ===="
    p = Pseudonym.find_by unique_id: ENV["CANVAS_LMS_ADMIN_EMAIL"]
    if p
        p.password = p.password_confirmation = ENV["CANVAS_LMS_ADMIN_PASSWORD"]
        p.save!
    else
        puts "====> ERROR - no admin user found! ===="
    end
    puts "==== END Resetting admin password ===="

    puts "====== OPE STARTUP_APPLY_ADMIN_SETTINGS END ======"
  end
  
  task :enable_auditing => :environment do
    puts "====== OPE ENABLE_AUDITING BEGIN ======"
	# Audit all tables in the db
	ActiveRecord::Base.connection.tables.each do |table|
	  begin
		# Don't add triggers to certain tables that we don't want to merge
		# TODO - ruby way to test against an array of table names?
		if (table != "delayed_jobs" && table != "failed_jobs")
			ActiveRecord::Base.connection.execute("select ope_audit.ope_audit_table('#{table}');")
			print "#{table} ENABLED, "
		else
			# Make sure to remove trigger if it exists
			ActiveRecord::Base.connection.execute("select ope_audit.ope_audit_table_disable('#{table}');")
			print "#{table} DISABLED, "
		end
	  rescue
		print "#{table} -- ERROR --, "
	  end
	end
    puts "====== OPE ENABLE_AUDITING END ======"
  end
  
  task :set_sequence_range => :environment do
    puts "====== OPE SET_SEQUENCE_RANGE BEGIN ======"
    # If no range defined, create one and set it
    range_file = "/usr/src/app/tmp/db_sequence_range"
    rangestart = 0
    # Use an epoch time (in minutes which is about 2/14/18) when we calculate a new rangestart
    epoch_time = 25310582 # 24675840
    school_id_range_max = 999_999  # This times the local_id_range is the full db range
    local_id_range = 1_000_000_000 # Use this to bump the schoo_id range up
    
    
    # Old values
    # *_000_000_000_000_000_000 - Shard Range
    # 0_***_***_*00_000_000_000 - School Range
    # 0_000_000_0**_***_***_*** - Local ID Range

    # Javascript - uses float to store ints, so max is 53 bits instead of 64?
    # 9_223_372_036_854_775_807 - Normal Max 64 bit int - for every language but JScript
    # 0_009_007_199_254_740_991 - Max safe int for jscript (jscript, you suck in so many ways)
    # 0_00*_000_000_000_000_000 - We push DB shards to this digit (0-9 shards possible)
    # 0_000_***_***_000_000_000 - Auto set School Range based on time of initial startup (rolls over after 2 years)
    # 0_000_000_000_***_***_*** - Leaves 1 bil ids for local tables and doesn't loose data due to jscript


    # Load the current value if it exists
    if File.file?(range_file) == true
        File.open(range_file, 'r') do |f|
            line = f.gets
            rangestart = line.to_i
        end
        puts "===== Range already defined #{rangestart}"
    end
    
    if rangestart <= 0 or rangestart > school_id_range_max
        # Calculate new range
        puts "===== Invalid range #{rangestart}, calculating new range"
        rangestart = Time.now.to_i / 60 # Seconds since 1970 - convert to minutes
        rangestart = rangestart - epoch_time # Subtract epoch to start range at 0
        # Make sure we are 1 to school_id_range_max
        while rangestart >= school_id_range_max
            # If we overflow, just reset the range, odds of id conflict on the second or
            # third time through are extremely small
            rangestart = (rangestart - school_id_range_max).abs
        end
        if rangestart < 0
            puts "=====> ERROR ERROR ERROR - rangestart calculated to negative number!!!!!"
            rangestart = 1
        end
        
        # Store the range in a file
        begin
            File.open(range_file, 'w') do |f|
                f.puts rangestart
            end
        rescue
            puts "Error writing DB ID range to file #{range_file}"
        end
    end
    
    # Bump the range up to to the school range - e.g. shift it left into the billions/trillions area
    rangestart_full = rangestart * local_id_range		

    # Update the database sequences to use this range
    ActiveRecord::Base.connection.tables.each do |table|  
        begin
            last_seq = 0
            seq_row = ActiveRecord::Base.connection.exec_query("select nextval('#{table}_id_seq'::regclass) as nv")
            seq_row.each do |row|
                last_seq = row["nv"].to_i
            end
            print "#{table} #{last_seq} -> #{rangestart_full}, "
            if (last_seq < rangestart_full || last_seq >= rangestart_full + local_id_range )
                # puts "=====> Last sequence outside of current range #{table} #{last_seq} -> #{rangestart_full}"
                ActiveRecord::Base.connection.execute("ALTER SEQUENCE #{table}_id_seq RESTART WITH #{rangestart_full}")
            end
        rescue
            puts "#{table} ERROR, "
        end
    end

    # Set the logged_actions table sequence too
    last_seq = 0
    seq_row = ActiveRecord::Base.connection.exec_query("select nextval('ope_audit.logged_actions_event_id_seq'::regclass) as nv")
    seq_row.each do |row|
        last_seq = row["nv"].to_i
    end
    if (last_seq < rangestart_full || last_seq >= rangestart_full + local_id_range )
        #puts "=====> Last sequence outside of current range logged_actions_event_id_seq #{last_seq} -> #{rangestart_full}"
        ActiveRecord::Base.connection.execute("ALTER SEQUENCE ope_audit.logged_actions_event_id_seq RESTART WITH #{rangestart_full}")
    end

    puts "=====> Finished setting sequence range to #{rangestart_full}"
    # Make sure to change the constraint on the version tables so they don't blow up with big ids
    begin
        ActiveRecord::Base.connection.exec_query("alter table versions_0 drop constraint versions_0_versionable_id_check;")
    rescue
    end
    begin
        ActiveRecord::Base.connection.exec_query("alter table versions_1 drop constraint versions_1_versionable_id_check;")
    rescue
    end
    
    puts "====== OPE SET_SEQUENCE_RANGE END ======"
  end
  
  
  task :init_auditing => :environment do
    puts "====== OPE INIT_AUDITING BEGIN ======"
    # Add the audit scheme/etc...
	ActiveRecord::Base.connection.execute( <<-SQLSTRING

CREATE SCHEMA IF NOT EXISTS ope_audit;
REVOKE ALL ON SCHEMA ope_audit FROM public;

COMMENT ON SCHEMA ope_audit IS 'Database sync code for Open Prison Education project';

CREATE OR REPLACE FUNCTION ope_audit.jsonb_minus ( arg1 jsonb, arg2 jsonb )
 RETURNS jsonb
AS $$

SELECT 
	COALESCE(json_object_agg(
        key,
        CASE
            -- if the value is an object and the value of the second argument is
            -- not null, we do a recursion
            WHEN jsonb_typeof(value) = 'object' AND arg2 -> key IS NOT NULL 
			THEN ope_audit.jsonb_minus(value, arg2 -> key)
            -- for all the other types, we just return the value
            ELSE value
        END
    ), '{}')::jsonb
FROM 
	jsonb_each(arg1)
WHERE 
	arg1 -> key <> arg2 -> key 
	OR arg2 -> key IS NULL

$$ LANGUAGE SQL;

DROP OPERATOR IF EXISTS - ( jsonb, jsonb );

CREATE OPERATOR - (
    PROCEDURE = ope_audit.jsonb_minus,
    LEFTARG   = jsonb,
    RIGHTARG  = jsonb );

SQLSTRING
	)
	
	# Run second part - split so operator can be in place when next statements run
	ActiveRecord::Base.connection.execute( <<-SQLSTRING
	
CREATE TABLE IF NOT EXISTS ope_audit.logged_actions (
    event_id bigserial primary key,
    schema_name text not null,
    table_name text not null,
    relid oid not null,
    session_user_name text,
    action_tstamp_tx TIMESTAMP WITH TIME ZONE NOT NULL,
    action_tstamp_stm TIMESTAMP WITH TIME ZONE NOT NULL,
    action_tstamp_clk TIMESTAMP WITH TIME ZONE NOT NULL,
    transaction_id bigint,
    application_name text,
    client_addr inet,
    client_port integer,
    client_query text,
    action TEXT NOT NULL CHECK (action IN ('I','D','U', 'T')),
    row_data jsonb,
    changed_fields jsonb,
    statement_only boolean not null
);

REVOKE ALL ON ope_audit.logged_actions FROM public;

COMMENT ON TABLE ope_audit.logged_actions IS 'History of auditable actions on audited tables, from audit.if_modified_func()';
COMMENT ON COLUMN ope_audit.logged_actions.event_id IS 'Unique identifier for each auditable event';
COMMENT ON COLUMN ope_audit.logged_actions.schema_name IS 'Database schema audited table for this event is in';
COMMENT ON COLUMN ope_audit.logged_actions.table_name IS 'Non-schema-qualified table name of table event occured in';
COMMENT ON COLUMN ope_audit.logged_actions.relid IS 'Table OID. Changes with drop/create. Get with ''tablename''::regclass';
COMMENT ON COLUMN ope_audit.logged_actions.session_user_name IS 'Login / session user whose statement caused the audited event';
COMMENT ON COLUMN ope_audit.logged_actions.action_tstamp_tx IS 'Transaction start timestamp for tx in which audited event occurred';
COMMENT ON COLUMN ope_audit.logged_actions.action_tstamp_stm IS 'Statement start timestamp for tx in which audited event occurred';
COMMENT ON COLUMN ope_audit.logged_actions.action_tstamp_clk IS 'Wall clock time at which audited event''s trigger call occurred';
COMMENT ON COLUMN ope_audit.logged_actions.transaction_id IS 'Identifier of transaction that made the change. May wrap, but unique paired with action_tstamp_tx.';
COMMENT ON COLUMN ope_audit.logged_actions.client_addr IS 'IP address of client that issued query. Null for unix domain socket.';
COMMENT ON COLUMN ope_audit.logged_actions.client_port IS 'Remote peer IP port address of client that issued query. Undefined for unix socket.';
COMMENT ON COLUMN ope_audit.logged_actions.client_query IS 'Top-level query that caused this auditable event. May be more than one statement.';
COMMENT ON COLUMN ope_audit.logged_actions.application_name IS 'Application name set when this audit event occurred. Can be changed in-session by client.';
COMMENT ON COLUMN ope_audit.logged_actions.action IS 'Action type; I = insert, D = delete, U = update, T = truncate';
COMMENT ON COLUMN ope_audit.logged_actions.row_data IS 'Record value. Null for statement-level trigger. For INSERT this is the new tuple. For DELETE and UPDATE it is the old tuple.';
COMMENT ON COLUMN ope_audit.logged_actions.changed_fields IS 'New values of fields changed by UPDATE. Null except for row-level UPDATE events.';
COMMENT ON COLUMN ope_audit.logged_actions.statement_only IS '''t'' if ope_audit event is from an FOR EACH STATEMENT trigger, ''f'' for FOR EACH ROW';

CREATE INDEX IF NOT EXISTS logged_actions_relid_idx ON ope_audit.logged_actions(relid);
CREATE INDEX IF NOT EXISTS logged_actions_action_tstamp_tx_stm_idx ON ope_audit.logged_actions(action_tstamp_stm);
CREATE INDEX IF NOT EXISTS logged_actions_action_idx ON ope_audit.logged_actions(action);
CREATE INDEX IF NOT EXISTS logged_actions_table_name_idx ON ope_audit.logged_actions(table_name);

CREATE OR REPLACE FUNCTION ope_audit.if_modified_func() RETURNS TRIGGER AS $body$
DECLARE
    ope_audit_row ope_audit.logged_actions;
    include_values boolean;
    log_diffs boolean;
    h_old jsonb;
    h_new jsonb;
    excluded_cols text[] = ARRAY[]::text[];
BEGIN
    IF TG_WHEN <> 'AFTER' THEN
        RAISE EXCEPTION 'ope_audit.if_modified_func() may only run as an AFTER trigger';
    END IF;

    ope_audit_row = ROW(
        nextval('ope_audit.logged_actions_event_id_seq'), -- event_id
        TG_TABLE_SCHEMA::text,                        -- schema_name
        TG_TABLE_NAME::text,                          -- table_name
        TG_RELID,                                     -- relation OID for much quicker searches
        session_user::text,                           -- session_user_name
        current_timestamp,                            -- action_tstamp_tx
        statement_timestamp(),                        -- action_tstamp_stm
        clock_timestamp(),                            -- action_tstamp_clk
        txid_current(),                               -- transaction ID
        current_setting('application_name'),          -- client application
        inet_client_addr(),                           -- client_addr
        inet_client_port(),                           -- client_port
        current_query(),                              -- top-level query or queries (if multistatement) from client
        substring(TG_OP,1,1),                         -- action
        NULL, NULL,                                   -- row_data, changed_fields
        'f'                                           -- statement_only
        );

    IF NOT TG_ARGV[0]::boolean IS DISTINCT FROM 'f'::boolean THEN
        ope_audit_row.client_query = NULL;
    END IF;

    IF TG_ARGV[1] IS NOT NULL THEN
        excluded_cols = TG_ARGV[1]::text[];
    END IF;

    IF (TG_OP = 'UPDATE' AND TG_LEVEL = 'ROW') THEN
        ope_audit_row.row_data = to_jsonb(OLD.*);
        ope_audit_row.changed_fields =  (to_jsonb(NEW.*) - to_jsonb(ope_audit_row.row_data)) - to_jsonb(excluded_cols);
        IF ope_audit_row.changed_fields = NULL THEN
            -- All changed fields are ignored. Skip this update.
            RETURN NULL;
        END IF;
    ELSIF (TG_OP = 'DELETE' AND TG_LEVEL = 'ROW') THEN
        ope_audit_row.row_data = to_jsonb(OLD.*) - to_jsonb(excluded_cols);
    ELSIF (TG_OP = 'INSERT' AND TG_LEVEL = 'ROW') THEN
        ope_audit_row.row_data = to_jsonb(NEW.*) - to_jsonb(excluded_cols);
    ELSIF (TG_LEVEL = 'STATEMENT' AND TG_OP IN ('INSERT','UPDATE','DELETE','TRUNCATE')) THEN
        ope_audit_row.statement_only = 't';
    ELSE
        RAISE EXCEPTION '[ope_audit.if_modified_func] - Trigger func added as trigger for unhandled case: %, %',TG_OP, TG_LEVEL;
        RETURN NULL;
    END IF;
    INSERT INTO ope_audit.logged_actions VALUES (ope_audit_row.*);
    RETURN NULL;
END;
$body$
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public;


COMMENT ON FUNCTION ope_audit.if_modified_func() IS $body$
Track changes to a table at the statement and/or row level.

Optional parameters to trigger in CREATE TRIGGER call:

param 0: boolean, whether to log the query text. Default 't'.

param 1: text[], columns to ignore in updates. Default [].

         Updates to ignored cols are omitted from changed_fields.

         Updates with only ignored cols changed are not inserted
         into the ope_audit log.

         Almost all the processing work is still done for updates
         that ignored. If you need to save the load, you need to use
         WHEN clause on the trigger instead.

         No warning or error is issued if ignored_cols contains columns
         that do not exist in the target table. This lets you specify
         a standard set of ignored columns.

There is no parameter to disable logging of values. Add this trigger as
a 'FOR EACH STATEMENT' rather than 'FOR EACH ROW' trigger if you do not
want to log row values.

Note that the user name logged is the login role for the session. The ope_audit trigger
cannot obtain the active role because it is reset by the SECURITY DEFINER invocation
of the ope_audit trigger its self.
$body$;

CREATE OR REPLACE FUNCTION ope_audit.ope_audit_table(target_table regclass, ope_audit_rows boolean, ope_audit_query_text boolean, ignored_cols text[]) RETURNS void AS $body$
DECLARE
  stm_targets text = 'INSERT OR UPDATE OR DELETE OR TRUNCATE';
  _q_txt text;
  _ignored_cols_snip text = '';
BEGIN
    EXECUTE 'DROP TRIGGER IF EXISTS ope_audit_trigger_row ON ' || target_table;
    EXECUTE 'DROP TRIGGER IF EXISTS ope_audit_trigger_stm ON ' || target_table;

    IF ope_audit_rows THEN
        IF array_length(ignored_cols,1) > 0 THEN
            _ignored_cols_snip = ', ' || quote_literal(ignored_cols);
        END IF;
        _q_txt = 'CREATE TRIGGER ope_audit_trigger_row AFTER INSERT OR UPDATE OR DELETE ON ' ||
                 target_table ||
                 ' FOR EACH ROW EXECUTE PROCEDURE ope_audit.if_modified_func(' ||
                 quote_literal(ope_audit_query_text) || _ignored_cols_snip || ');';
        RAISE NOTICE '%',_q_txt;
        EXECUTE _q_txt;
        stm_targets = 'TRUNCATE';
    ELSE
    END IF;

    _q_txt = 'CREATE TRIGGER ope_audit_trigger_stm AFTER ' || stm_targets || ' ON ' ||
             target_table ||
             ' FOR EACH STATEMENT EXECUTE PROCEDURE ope_audit.if_modified_func('||
             quote_literal(ope_audit_query_text) || ');';
    RAISE NOTICE '%',_q_txt;
    EXECUTE _q_txt;

END;
$body$
language 'plpgsql';

CREATE OR REPLACE FUNCTION ope_audit.ope_audit_table_disable(target_table regclass) RETURNS void AS $body$
DECLARE
  stm_targets text = 'INSERT OR UPDATE OR DELETE OR TRUNCATE';
  _q_txt text;
  _ignored_cols_snip text = '';
BEGIN
    EXECUTE 'DROP TRIGGER IF EXISTS ope_audit_trigger_row ON ' || target_table;
    EXECUTE 'DROP TRIGGER IF EXISTS ope_audit_trigger_stm ON ' || target_table;
END;
$body$
language 'plpgsql';

COMMENT ON FUNCTION ope_audit.ope_audit_table(regclass, boolean, boolean, text[]) IS $body$
Add auditing support to a table.

Arguments:
   target_table:     Table name, schema qualified if not on search_path
   ope_audit_rows:       Record each row change, or only audit at a statement level
   ope_audit_query_text: Record the text of the client query that triggered the audit event?
   ignored_cols:     Columns to exclude from update diffs, ignore updates that change only ignored cols.
$body$;

-- Pg doesn't allow variadic calls with 0 params, so provide a wrapper
CREATE OR REPLACE FUNCTION ope_audit.ope_audit_table(target_table regclass, ope_audit_rows boolean, ope_audit_query_text boolean) RETURNS void AS $body$
SELECT ope_audit.ope_audit_table($1, $2, $3, ARRAY[]::text[]);
$body$ LANGUAGE SQL;

-- And provide a convenience call wrapper for the simplest case
-- of row-level logging with no excluded cols and query logging enabled.
--
CREATE OR REPLACE FUNCTION ope_audit.ope_audit_table(target_table regclass) RETURNS void AS $$
SELECT ope_audit.ope_audit_table($1, BOOLEAN 't', BOOLEAN 't');
$$ LANGUAGE 'sql';

COMMENT ON FUNCTION ope_audit.ope_audit_table(regclass) IS $body$
Add ope_auditing support to the given table. Row-level changes will be logged with full client query text. No cols are ignored.
$body$;
	
	
SQLSTRING
	)
    
    puts "====== OPE INIT_AUDITING END ======"
  end
  
  task :ensure_jwk_key => :environment do
    puts "====== OPE ENSURE_JWK_KEY BEGIN ======"
    # Create a JWK key for the system if it doesn't exist
    # Look in keys folder for a .key file
    keys_folder = Rails.root.join("keys")
    puts "Using keys folder: #{keys_folder}"

    # Check if the keys folder exists, if not create it
    unless Dir.exists?(keys_folder)
        puts "Keys folder not found. Creating keys folder..."
        Dir.mkdir(keys_folder)
    end

    # Get the count of .jwk files in the keys folder
    jwk_files = Dir[keys_folder.join("*.jwk")]
    jwk_count = jwk_files.count
    puts "Number of .jwk files: #{jwk_count}"

    if jwk_count < 1
        puts "No JWK keys found. Generating a new key..."
        key_id = Time.now.utc.iso8601
        key = OpenSSL::PKey::RSA.generate(2048)
        jwk = key.to_jwk(kid: key_id)
        puts "Generated JWK key: #{jwk}"
        File.write(keys_folder.join("#{key_id}.jwk"), jwk.to_json)
    #else
    #    puts "JWK key found. Skipping generation..."
    end
    
    # Load the keys into the dynamic settings.yml template
    jwk_files = Dir[keys_folder.join("*.jwk")]

    puts "Found keys: #{jwk_files}"
    jwk_keys = {} #Struct.new(:key, :value)

    jwk_files.each do |key_file|
        puts "====> Found JWK key: #{key_file}"
        #jwk_keys.add(JSON.parse(File.read(key_file)))
        key = File.basename(key_file, ".jwk")
        # Need to store in "{\"key\":\"value\"}" format
        jwk_keys[key] = JSON.parse(File.read(key_file))
    end

    # Build the string for the dynamic settings.yml file
    canvas_jwk_keys = ""
    # Needs to be past, present, future keys - just save the last one for now
    for key in jwk_keys.keys
        # Yes - clear it so we only keep the last key we load
        canvas_jwk_keys = ""
        key_str = jwk_keys[key].to_json.gsub('"', '\"')
        #safe_key = key.gsub("-", "_").gsub(".", "_").gsub(":", "_")
        #canvas_jwk_keys += "        jwk-#{safe_key}.json: \"#{key_str}\"\n"
        canvas_jwk_keys += "        jwk-past.json: \"#{key_str}\"\n"
        canvas_jwk_keys += "        jwk-present.json: \"#{key_str}\"\n"
        canvas_jwk_keys += "        jwk-future.json: \"#{key_str}\"\n"
    end
    
    #replace <CANVAS_JWK_KEYS> dynamic_settings value with key array
    dynamic_settings = File.read(Rails.root.join("config", "dynamic_settings.yml"))
    dynamic_settings = dynamic_settings.gsub("#<CANVAS_JWK_KEYS>", canvas_jwk_keys)
    File.write(Rails.root.join("config", "dynamic_settings.yml"), dynamic_settings)
    
    puts "====== OPE ENSURE_JWK_KEY END ======"
  end
    
end
