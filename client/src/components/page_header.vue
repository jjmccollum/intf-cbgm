<template>


<div>
  <b-navbar type="dark" variant="dark">
    <b-navbar-nav>
      <b-nav-item href="#">Home</b-nav-item>

      <!-- Navbar dropdowns -->
      <b-nav-item-dropdown text="Lang" right>
        <b-dropdown-item href="#">EN</b-dropdown-item>
        <b-dropdown-item href="#">ES</b-dropdown-item>
        <b-dropdown-item href="#">RU</b-dropdown-item>
        <b-dropdown-item href="#">FA</b-dropdown-item>
      </b-nav-item-dropdown>

      <b-nav-item-dropdown v-for="i of $store.state.instances" :key="i.application_name" :text="i.application_name" right>
        <b-dropdown-item href="#">EN</b-dropdown-item>
        <b-dropdown-item href="#">ES</b-dropdown-item>
        <b-dropdown-item href="#">RU</b-dropdown-item>
        <b-dropdown-item href="#">FA</b-dropdown-item>
      </b-nav-item-dropdown>


      <b-nav-item-dropdown text="User" right>
        <b-dropdown-item href="#">Account</b-dropdown-item>
        <b-dropdown-item href="#">Settings</b-dropdown-item>
      </b-nav-item-dropdown>
    </b-navbar-nav>
  </b-navbar>
</div>
</template>

<script>
/**
 * The page header with the violet ribbon.
 *
 * @component client/page_header
 * @author Marcello Perathoner
 */

import { mapGetters } from "vuex";
import { BNavbar } from 'bootstrap-vue/src/components/navbar/navbar';
import { BNavbarNav } from 'bootstrap-vue/src/components/navbar/navbar-nav';
import { BNavItem } from 'bootstrap-vue/src/components/nav/nav-item';
import { BNavItemDropdown } from 'bootstrap-vue/src/components/nav/nav-item-dropdown';
import { BDropdownItem } from 'bootstrap-vue/src/components/dropdown/dropdown-item';

export default {
    'components' : {
      'b-navbar'            : BNavbar,
      'b-navbar-nav'        : BNavbarNav,
      'b-nav-item'          : BNavItem,
      'b-nav-item-dropdown' : BNavItemDropdown,
      'b-dropdown-item'     : BDropdownItem,
  },
  data() {
    return {};
  },
  computed: {
    ...mapGetters([
      "can_read",
      "is_logged_in",
      "current_application",
      "current_user",
      "route_meta"
    ])
  }
};
</script>

<style lang="scss">
/* page_header.vue */
@import "bootstrap-custom";

div.vm-page-header {
  background-color: #d2d2d2;
  margin-bottom: 2rem;

  div.bs-docs-header {
    margin: 0;
    padding: ($spacer * 0.5) 0 ($spacer * 0.25) 0;
    color: var(--light);
    background-color: var(--brand-color);

    @media print {
      /* compensate for missing div.login-nav */
      margin-bottom: $spacer;
      color: black;
      background-color: transparent;
    }
  }

  div.bs-docs-container {
    padding-top: ($spacer * 0.5);
    padding-bottom: ($spacer * 0.5);
  }

  div.login-nav {
    @media print {
      display: none !important;
    }
    a, span {
      font-size: 18px;
    }
  }

  div.login-required-message {
    color: red;
  }
}
</style>
