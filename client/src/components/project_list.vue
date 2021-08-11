<template>
  <div class="vm-project-list">
    <div class="container bs-docs-container">
      <div class="jumbotron">
        <h1 class="display-4">A program suite for doing CBGM</h1>
        <p class="lead">Coherence-Based Genealogical Method (CBGM)</p>
        <hr class="my-4">
        <img :src="ECMActs" style="float: left; width: 200px; margin: 0 1rem 1rem 0"/>
        <p>The <strong>Coherence-Based Genealogical Method</strong>, developed by Gerd Mink at the
        Institut für Neutestamentliche Textforschung (INTF) in Münster, aims at a
        scientifically founded reconstruction<br>of the initial text (*Ausgangstext*) of
        the New Testament tradition, i.e. a hypothesis about the text from which the 
        manuscript transmission started.<br>The fundamental problem posed by the nature
        of the New Testament manuscript tradition is known as contamination, the 
        mutual influence of different strands of transmission on each other.<br>
        Contamination renders the application of conventional stemmatics impossible, 
        and the New Testament manuscript tradition is known to be highly contaminated.<br>
        The CBGM, however, offers a cure for contamination, thanks to three essential 
        principles distinguishing it from conventional stemmatics.</p>
        <br>
        <a class="btn btn-primary btn-lg" href="http://egora.uni-muenster.de/intf/projekte/gsm_aus_en.shtml" target="_blank" role="button">Learn more</a>
      </div>
    </div>
    <div class="container bs-docs-container">
      <h4>Currently online projects</h4>
      <br>
      <table class="table table-bordered table-hover">
        <tbody>
          <tr>
            <th>Project</th><th>Editable</th><th>Description</th><th>Guide</th>
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
            <td class="guide">
              <div v-if="i.application_name.includes('Acts')">
              <a href="/pdfs/GenQ4_Guide.pdf" target="_blank">Short Guide (PDF) for Acts</a>
              </div>
              <div v-if="i.application_name.includes('Mark')">
              <a href="/pdfs/Short_Guide_CBGM_Mark_KW.pdf" target="_blank">Short Guide (PDF) for Mark</a>
              </div>
            </td>
          </router-link>
        </tbody>
      </table>

      <br><br>
      <h4>Docker Installation</h4>
      <p>
      <ol>
      <li>Install the free community version of Docker:</li>
        <ul>
        <li>for Windows see: <a href="https://docs.docker.com/docker-for-windows/install/" target="_blank">Docker for Windows</a></li>
        <li>for Mac see:  <a href="https://docs.docker.com/docker-for-mac/install/" target="_blank">Docker for Mac</a></li>
        <li>for Debian Linux see:  <a href="https://docs.docker.com/compose/install/" target="_blank">Docker for Debian Linux</a></li>
        </ul>
    
    
    

<li>Create a new directory and change into it.</li>
<li>Download <a href="https://raw.githubusercontent.com/SCDH/intf-cbgm/master/docker/docker-compose.yml" target="_blank">https://raw.githubusercontent.com/SCDH/intf-cbgm/master/docker/docker-compose.yml</a></li>

<li>Run:

    <code>docker-compose up</code><br>

This will download the Docker containers and initialize the database. It will take some time depending on your internet connection speed and your PC.</li>

<li>Test the installation: Point your browser to the url: <a href="http://localhost:5000" target="_blank">http://localhost:5000</a> and use the application.</li>

<li>When satisfied, hit Ctrl+C to stop the Docker service.</li>

</ol>

<strong>Note</strong>: All newest docker images can be found at <a href="https://hub.docker.com/r/scdh" target="_blank">https://hub.docker.com/r/scdh</a><br>
<a href="https://hub.docker.com/r/scdh/intf-cbgm-app-server" target="_blank">intf-cbgm-app-server</a><br>
<a href="https://hub.docker.com/r/scdh/intf-cbgm-db-server" target="_blank">intf-cbgm-db-server</a><br>
      
      </p>

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
        <a href="https://www.uni-muenster.de/de/en/datenschutzerklaerung.html"
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
import actsguide from "../images/actsguide.jpg";
import markguide from "../images/markguide.jpg";
import ECMActs from "../images/ECMActs.jpg";

export default {
  data: function() {
    return {
      intf_logo: intf_logo,
      awk_logo: awk_logo,
      cceh_logo: cceh_logo,
      scdh_logo: scdh_logo,
      markguide: markguide,
      actsguide: actsguide,
      ECMActs: ECMActs
    };
  }
};
</script>

<style lang="scss">
/* project_list.vue */

div.vm-project-list {

    .img-guide {
      height: 200px;
    }

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
