<template>
  <div class="vm-project-list">
    <div class="container bs-docs-container">
      <h4>Currently available projects</h4>
      <br>
      <table class="table table-bordered table-hover">
        <tbody>
          <tr>
            <th>Project</th><th>Editable</th><th>Description</th>
          </tr>
          <router-link v-for="i of $store.state.instances" :key="i.application_root"
                       tag="tr" :to="'/' + i.application_root">
            <td class="app_name">
              <a>{{ i.application_name }}</a>
            </td>
            <td class="can_edit">
              <span v-if="i.user_can_write" class="fas fa-pen-square" />
            </td>
            <td class="app_desc">
              {{ i.application_description }}
            </td>
          </router-link>
        </tbody>
      </table>

      <br><br>
      <h4>Partners</h4>
      <div class="container logos">
          <div class="row">
              <div class="col-sm-3">
              <a href="http://egora.uni-muenster.de/intf/index_en.shtml"
          ><img :src="intf_logo"
        /></a>
              </div>
              <div class="col-sm-3">
              <a href="http://www.awk.nrw.de"><img :src="awk_logo"/></a></div>
              <div class="col-sm-3">
              <a href="http://cceh.uni-koeln.de"><img :src="cceh_logo"/></a></div>
              <div class="col-sm-3">
              <a href="https://www.uni-muenster.de/SCDH/"><img :src="scdh_logo"/></a></div>
          </div>
      </div>

      <br><br>
      <div class="gdpr">
        <a href="https://www.portal.uni-koeln.de/datenschutz1.html"
          >Data Privacy Statement</a
        >
      </div>
    </div>
  </div>
</template>



<script>
/**
 * Project list component.  List the available projects.
 *
 * A project is one book of the NT and one phase.
 *
 * @component client/project_list
 * @author Marcello Perathoner
 */
/* import these images for the side-effect only: make webpack pack these files. */
import intf_logo from "../images/intf2021.jpeg";
import awk_logo from "../images/awk-logo-00.png";
import cceh_logo from "../images/cceh-logo.png";
import scdh_logo from "../images/scdh-logo.jpg";

export default {
  data: function() {
    return {
      intf_logo: intf_logo,
      awk_logo: awk_logo,
      cceh_logo: cceh_logo,
      scdh_logo: scdh_logo
    };
  }
};
</script>

<style lang="scss">
/* project_list.vue */

div.vm-project-list {
    td.app_name {
        width: 20%;
    }

    td.can_edit {
        width: 1%;
    }

    span.fas {
        font-size: 150%;
        color: red;
    }

    table {
        margin-top: 2em;
    }

    div.logos {
    margin-top: 2em;

    img {
      height: 100px;
      padding-right: 1em;
    }
  }
}

</style>
