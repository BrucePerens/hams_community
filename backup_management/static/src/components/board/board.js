/** @odoo-module **/
import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class BackupBoard extends Component {
    setup() {
        this.orm = useService("orm");
        this.website = useService("website");
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

    async triggerBackup(configId) {
        await this.orm.call("backup.config", "action_trigger_backup", [configId]);
        await this.fetchData();
    }

    async syncSnapshots(configId) {
        await this.orm.call("backup.config", "action_sync_snapshots", [configId]);
        await this.fetchData();
    }

    async fetchData() {
        // Isolation by website_id
        const context = {};
        if (this.website.currentWebsite) {
            context.website_id = this.website.currentWebsite.id;
        }
        this.state.configs = await this.orm.call("backup.config", "get_board_data", [], { context: context });
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
