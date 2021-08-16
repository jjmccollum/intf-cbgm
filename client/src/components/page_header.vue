<template>
  <div class="container nav-header">
    <b-navbar>
      <img
        src="images/wwu_logo.svg"
        style="float:left; width:280px; margin-right: 1rem;"
      />
      <img
        src="images/intf2021.jpeg"
        style="position: absolute; right: 0; margin: 0;"
      />
    </b-navbar>
    <b-navbar class="main-nav">
      <b-navbar-nav>
        <b-nav-item href="/">Home</b-nav-item>

        <b-nav-item-dropdown
          v-for="i of $store.state.instances"
          :key="i.application_name"
          :text="i.application_name"
          right
        >
          <b-dropdown-item href="#">Coherence and Textual Flow</b-dropdown-item>
          <b-dropdown-item href="#">Comparison of Witnesses</b-dropdown-item>
          <b-dropdown-item href="#">Find Relatives</b-dropdown-item>
        </b-nav-item-dropdown>
      <b-nav-item style="position: absolute; right:0;" href="/user/sign-in">Sign In</b-nav-item>

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
import { BNavbar } from "bootstrap-vue/src/components/navbar/navbar";
import { BNavbarNav } from "bootstrap-vue/src/components/navbar/navbar-nav";
import { BNavItem } from "bootstrap-vue/src/components/nav/nav-item";
import { BNavItemDropdown } from "bootstrap-vue/src/components/nav/nav-item-dropdown";
import { BDropdownItem } from "bootstrap-vue/src/components/dropdown/dropdown-item";

export default {
  components: {
    "b-navbar": BNavbar,
    "b-navbar-nav": BNavbarNav,
    "b-nav-item": BNavItem,
    "b-nav-item-dropdown": BNavItemDropdown,
    "b-dropdown-item": BDropdownItem
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

.nav-header {
  margin-bottom: 3rem;
}

.main-nav {
  border-bottom: 4px solid;
}

ul.navbar-nav li.nav-item a.nav-link {
  font-family: Metawebpro, Verdana, sans-serif;
  text-transform: uppercase;
  color: black;
  font-size: 20px;
  font-style: normal;
  font-weight: 400;
}

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
    a,
    span {
      font-size: 18px;
    }
  }

  div.login-required-message {
    color: red;
  }
}
</style>
