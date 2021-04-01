from mgmt_EventLog import EventLog

# NOTE - use import this way to avoid circular import errors
import mgmt_Computer
import mgmt_RegistrySettings

from color import strip_color_codes

def p_state(txt="", end=True, state="WORKING", title="UPDATING", kill_logon=False):
    # Print to the OPE-STATE logger
    l = EventLog.get_ope_state_instance()

    # Save the state in the registry
    if not state.lower() == "none":
        # Don't change the state if it is "none"
        mgmt_RegistrySettings.RegistrySettings.set_reg_value(value_name="ope_state", value=state)

    mgmt_RegistrySettings.RegistrySettings.set_reg_value(value_name="ope_state_title", value=title)

    
    
    txt = str(txt)
    txt = strip_color_codes(txt)
    l.info(txt)
    l.flush()
    
    try:
        mgmt_Computer.Computer.render_lock_screen(None, header=title, state=state)
    except Exception as ex:
        import color
        color.p("Error rendering lockscreen in p_state: " + str(ex))
    
    # try:
    #     mgmt_Computer.Computer.set_lock_screen_image(kill_logon=kill_logon)
    # except Exception as ex:
    #     import color
    #     color.p("Error setting lockscreen in p_state: " + str(ex))

    # Can't set desktop when not logged in?
    # try:
    #     #mgmt_Computer.Computer.set_desktop_image()
    # except Exception as ex:
    #     import color
    #     color.p("Error setting desktop in in p_state: " + str(ex))
    
    return True
    

if __name__ == "__main__":
    p_state("test...")
    #p_state("Really long line2  the quick brown fox jumped over the fence. the quick brown fox jumped over the fence. the quick brown fox jumped over the fence. the quick brown fox jumped over the fence. the quick brown fox jumped over the fence. the quick brown fox jumped over the fence. the quick brown fox jumped over the fence. ")
