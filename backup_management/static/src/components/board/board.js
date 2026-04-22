/** @odoo-module **/
import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class BackupBoard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            configs: [],
            transformStyle: ""
        });

        onMounted(async () => {
            await this.fetchData();
            this.burnInTimer = setInterval(() => this.applyBurnInShift(), 60000);
        });

        onWillUnmount(() => {
            if (this.burnInTimer) clearInterval(this.burnInTimer);
        });
    }

    async fetchData() {
        this.state.configs = await this.orm.call("backup.config", "get_board_data", []);
        this.applyBurnInShift();
    }

    applyBurnInShift() {
        const x = Math.floor(Math.random() * 30) - 15;
        const y = Math.floor(Math.random() * 30) - 15;
        this.state.transformStyle = `transform: translate(${x}px, ${y}px); transition: transform 20s linear;`;
    }
}
BackupBoard.template = "backup_management.BackupBoardTemplate";
registry.category("actions").add("backup_management.board", BackupBoard);
