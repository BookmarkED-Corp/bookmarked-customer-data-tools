const express = require('express');
const fs = require('fs').promises;
const path = require('path');
const cors = require('cors');
const Anthropic = require('@anthropic-ai/sdk');

const app = express();
const PORT = 9001;

app.use(cors());
app.use(express.json());
app.use(express.static('.'));

const KANBAN_DIR = path.join(__dirname, 'kanban');
const COLUMNS = ['backlog', 'ready', 'in_progress', 'review', 'done'];

// Initialize Anthropic client
const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || ''
});

// Helper function to parse markdown with YAML frontmatter
function parseMarkdownTask(content) {
  const parts = content.split('---\n');
  if (parts.length < 3) {
    throw new Error('Invalid markdown format: missing frontmatter');
  }

  const frontmatter = parts[1];
  const markdown = parts.slice(2).join('---\n');

  // Parse frontmatter
  const task = {};
  frontmatter.split('\n').forEach(line => {
    if (line.includes(':')) {
      const [key, ...valueParts] = line.split(':');
      const value = valueParts.join(':').trim();

      // Handle different value types
      if (value.toLowerCase() === 'null') {
        task[key.trim()] = null;
      } else if (value.toLowerCase() === 'true') {
        task[key.trim()] = true;
      } else if (value.toLowerCase() === 'false') {
        task[key.trim()] = false;
      } else if (value.startsWith('[') && value.endsWith(']')) {
        // Parse array
        if (value === '[]') {
          task[key.trim()] = [];
        } else {
          const items = value.slice(1, -1).split(',').map(i => i.trim());
          task[key.trim()] = items;
        }
      } else {
        task[key.trim()] = value;
      }
    }
  });

  // Parse markdown sections
  const sections = {};
  let currentSection = null;
  let currentContent = [];

  markdown.split('\n').forEach(line => {
    if (line.startsWith('## ')) {
      if (currentSection) {
        sections[currentSection] = currentContent.join('\n');
      }
      currentSection = line.substring(3).trim();
      currentContent = [];
    } else if (currentSection) {
      currentContent.push(line);
    }
  });

  if (currentSection) {
    sections[currentSection] = currentContent.join('\n');
  }

  // Extract structured data from sections
  if (sections['Description']) {
    task.description = sections['Description'].trim();
  }

  if (sections['Use Case']) {
    task.use_case = sections['Use Case'].trim();
  }

  if (sections['Acceptance Criteria']) {
    task.acceptance_criteria = [];
    sections['Acceptance Criteria'].split('\n').forEach(line => {
      line = line.trim();
      if (line.startsWith('- [')) {
        task.acceptance_criteria.push(line.substring(6).trim());
      }
    });
  }

  if (sections['Notes']) {
    task.notes = [];
    sections['Notes'].split('\n').forEach(line => {
      line = line.trim();
      if (line.startsWith('- ') || line.startsWith('* ')) {
        task.notes.push(line.substring(2).trim());
      }
    });
  }

  if (sections['Subtasks']) {
    task.subtasks = [];
    sections['Subtasks'].split('\n').forEach(line => {
      line = line.trim();
      if (line.startsWith('- [x]') || line.startsWith('- [X]')) {
        task.subtasks.push({ title: line.substring(6).trim(), completed: true });
      } else if (line.startsWith('- [ ]')) {
        task.subtasks.push({ title: line.substring(6).trim(), completed: false });
      }
    });
  }

  task.test_data = { good_samples: [], bad_samples: [] };

  return task;
}

// Helper function to convert task to markdown
function taskToMarkdown(task) {
  let md = '---\n';
  md += `id: ${task.id}\n`;
  md += `title: ${task.title}\n`;
  md += `type: ${task.type || 'feature'}\n`;
  md += `priority: ${task.priority || 'medium'}\n`;
  md += `assignee: ${task.assignee || 'unassigned'}\n`;
  md += `validation_status: ${task.validation_status || 'pending'}\n`;
  md += `created_at: ${task.created_at || ''}\n`;
  md += `updated_at: ${task.updated_at || ''}\n`;
  md += `completed_at: ${task.completed_at || 'null'}\n`;

  const tags = task.tags || [];
  md += `tags: [${Array.isArray(tags) ? tags.join(', ') : tags}]\n`;
  md += '---\n\n';

  md += `# ${task.title}\n\n`;
  md += `## Description\n\n`;
  md += `${task.description || 'No description provided'}\n\n`;

  md += `## Use Case\n\n`;
  md += `${task.use_case || '_No use case specified_'}\n\n`;

  md += `## Acceptance Criteria\n\n`;
  if (task.acceptance_criteria && task.acceptance_criteria.length > 0) {
    task.acceptance_criteria.forEach(criterion => {
      md += `- [ ] ${criterion}\n`;
    });
  } else {
    md += `_No criteria specified yet_\n`;
  }
  md += `\n`;

  md += `## Test Data\n\n`;
  md += `### Good Samples\n`;
  md += `_No good samples defined_\n\n`;
  md += `### Bad Samples\n`;
  md += `_No bad samples defined_\n\n`;

  md += `## Subtasks\n\n`;
  if (task.subtasks && task.subtasks.length > 0) {
    task.subtasks.forEach(subtask => {
      const checkbox = subtask.completed ? '[x]' : '[ ]';
      md += `- ${checkbox} ${subtask.title}\n`;
    });
  } else {
    md += `_No subtasks defined_\n`;
  }
  md += `\n`;

  md += `## Notes\n\n`;
  if (task.notes && task.notes.length > 0) {
    task.notes.forEach(note => {
      md += `- ${note}\n`;
    });
  } else {
    md += `_No notes yet_\n`;
  }

  return md;
}

// Helper function to read all tasks
async function getAllTasks() {
  const board = {
    backlog: [],
    ready: [],
    in_progress: [],
    review: [],
    done: []
  };

  for (const column of COLUMNS) {
    const columnPath = path.join(KANBAN_DIR, column);
    try {
      const files = await fs.readdir(columnPath);
      const mdFiles = files.filter(f => f.endsWith('.md'));

      for (const file of mdFiles) {
        const filePath = path.join(columnPath, file);
        const content = await fs.readFile(filePath, 'utf-8');
        const task = parseMarkdownTask(content);
        board[column].push(task);
      }

      // Sort by task ID
      board[column].sort((a, b) => {
        const numA = parseInt(a.id.split('-')[1]);
        const numB = parseInt(b.id.split('-')[1]);
        return numA - numB;
      });
    } catch (err) {
      console.error(`Error reading column ${column}:`, err);
    }
  }

  return board;
}

// Helper function to find task file
async function findTaskFile(taskId) {
  for (const column of COLUMNS) {
    const columnPath = path.join(KANBAN_DIR, column);
    const filePath = path.join(columnPath, `${taskId}.md`);
    try {
      await fs.access(filePath);
      return { column, filePath };
    } catch (err) {
      // File doesn't exist in this column, continue
    }
  }
  return null;
}

// Helper function to read project context
async function getProjectContext() {
  try {
    const requirementsPath = path.join(__dirname, 'REQUIREMENTS.md');
    const projectInfoPath = path.join(__dirname, '.claude', 'project_info.md');

    const requirements = await fs.readFile(requirementsPath, 'utf-8');
    const projectInfo = await fs.readFile(projectInfoPath, 'utf-8');

    return {
      requirements: requirements.substring(0, 5000), // Limit context size
      projectInfo: projectInfo.substring(0, 3000)
    };
  } catch (err) {
    console.error('Error reading project context:', err);
    return { requirements: '', projectInfo: '' };
  }
}

// API Routes

// Get all tasks organized by column
app.get('/api/board', async (req, res) => {
  try {
    const board = await getAllTasks();
    res.json(board);
  } catch (err) {
    console.error('Error getting board:', err);
    res.status(500).json({ error: 'Failed to load board' });
  }
});

// Get specific task
app.get('/api/task/:id', async (req, res) => {
  try {
    const taskLocation = await findTaskFile(req.params.id);
    if (!taskLocation) {
      return res.status(404).json({ error: 'Task not found' });
    }

    const content = await fs.readFile(taskLocation.filePath, 'utf-8');
    const task = parseMarkdownTask(content);
    res.json({ task, column: taskLocation.column });
  } catch (err) {
    console.error('Error getting task:', err);
    res.status(500).json({ error: 'Failed to load task' });
  }
});

// Update task
app.put('/api/task/:id', async (req, res) => {
  try {
    const taskLocation = await findTaskFile(req.params.id);
    if (!taskLocation) {
      return res.status(404).json({ error: 'Task not found' });
    }

    const updatedTask = {
      ...req.body,
      updated_at: new Date().toISOString()
    };

    const markdown = taskToMarkdown(updatedTask);

    await fs.writeFile(
      taskLocation.filePath,
      markdown,
      'utf-8'
    );

    res.json({ success: true, task: updatedTask });
  } catch (err) {
    console.error('Error updating task:', err);
    res.status(500).json({ error: 'Failed to update task' });
  }
});

// Move task to different column
app.post('/api/task/:id/move', async (req, res) => {
  try {
    const { toColumn } = req.body;

    if (!COLUMNS.includes(toColumn)) {
      return res.status(400).json({ error: 'Invalid column' });
    }

    const taskLocation = await findTaskFile(req.params.id);
    if (!taskLocation) {
      return res.status(404).json({ error: 'Task not found' });
    }

    if (taskLocation.column === toColumn) {
      return res.json({ success: true, message: 'Task already in target column' });
    }

    // Read task
    const content = await fs.readFile(taskLocation.filePath, 'utf-8');
    const task = parseMarkdownTask(content);

    // Update task metadata
    task.updated_at = new Date().toISOString();
    if (toColumn === 'done' && !task.completed_at) {
      task.completed_at = new Date().toISOString();
      task.validation_status = 'passed';
    }

    // Write to new location
    const newPath = path.join(KANBAN_DIR, toColumn, `${task.id}.md`);
    const markdown = taskToMarkdown(task);
    await fs.writeFile(newPath, markdown, 'utf-8');

    // Delete from old location
    await fs.unlink(taskLocation.filePath);

    res.json({ success: true, task, newColumn: toColumn });
  } catch (err) {
    console.error('Error moving task:', err);
    res.status(500).json({ error: 'Failed to move task' });
  }
});

// AI Enhancement endpoint
app.post('/api/ai/enhance', async (req, res) => {
  try {
    const { taskId, prompt, conversationHistory = [] } = req.body;

    if (!process.env.ANTHROPIC_API_KEY) {
      return res.status(400).json({
        error: 'ANTHROPIC_API_KEY not set. Please set it in your environment.'
      });
    }

    // Get task details
    const taskLocation = await findTaskFile(taskId);
    let taskContext = '';
    if (taskLocation) {
      const content = await fs.readFile(taskLocation.filePath, 'utf-8');
      const task = parseMarkdownTask(content);
      taskContext = `Current Task (${task.id}):\nTitle: ${task.title}\nDescription: ${task.description}\nType: ${task.type}\nPriority: ${task.priority}\nStatus: ${taskLocation.column}\n`;

      if (task.acceptance_criteria && task.acceptance_criteria.length > 0) {
        taskContext += `\nAcceptance Criteria:\n${task.acceptance_criteria.map((c, i) => `${i + 1}. ${c}`).join('\n')}`;
      }

      if (task.notes && task.notes.length > 0) {
        taskContext += `\nNotes:\n${task.notes.join('\n')}`;
      }
    }

    // Get project context
    const projectContext = await getProjectContext();

    // Build system message
    const systemMessage = `You are an AI assistant helping with task management for the Bookmarked SIS Integration Service v2 project.

Project Context:
${projectContext.projectInfo}

Requirements Summary (first 5000 chars):
${projectContext.requirements}

${taskContext}

Your role is to help refine, enhance, and discuss tasks in relation to the rest of the project. You can:
- Break down complex tasks into subtasks
- Suggest acceptance criteria
- Identify dependencies on other parts of the project
- Recommend implementation approaches
- Point out potential issues or considerations
- Help clarify requirements

Be concise and actionable in your responses.`;

    // Build messages array
    const messages = [
      ...conversationHistory,
      { role: 'user', content: prompt }
    ];

    // Call Claude API
    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 2048,
      system: systemMessage,
      messages: messages
    });

    const assistantMessage = response.content[0].text;

    res.json({
      success: true,
      response: assistantMessage,
      conversationHistory: [
        ...conversationHistory,
        { role: 'user', content: prompt },
        { role: 'assistant', content: assistantMessage }
      ]
    });

  } catch (err) {
    console.error('Error with AI enhancement:', err);
    res.status(500).json({ error: err.message || 'Failed to get AI response' });
  }
});

// Get board metadata
app.get('/api/metadata', async (req, res) => {
  try {
    const metadataPath = path.join(KANBAN_DIR, 'board-metadata.json');
    const content = await fs.readFile(metadataPath, 'utf-8');
    const metadata = JSON.parse(content);
    res.json(metadata);
  } catch (err) {
    console.error('Error getting metadata:', err);
    res.status(500).json({ error: 'Failed to load metadata' });
  }
});

// === TEST EXECUTION ENDPOINTS ===

const { spawn } = require('child_process');
const { v4: uuidv4 } = require('uuid');

// Install uuid if not already: npm install uuid

const TEST_RESULTS_DIR = path.join(__dirname, 'test-results');
const testRunsInProgress = new Map();

// List all available tests
app.get('/api/tests/list', async (req, res) => {
  try {
    const { exec } = require('child_process');
    const util = require('util');
    const execPromise = util.promisify(exec);

    let stdout = '';
    try {
      const result = await execPromise('source venv/bin/activate && python -m pytest --collect-only -q tests/', {
        cwd: __dirname,
        shell: '/bin/bash'
      });
      stdout = result.stdout;
    } catch (err) {
      // pytest --collect-only can exit with code 2 due to warnings, but still outputs tests
      // Parse stdout if it contains test data
      if (err.stdout && err.stdout.includes('::')) {
        stdout = err.stdout;
      } else {
        throw err;
      }
    }

    const tests = stdout.split('\n')
      .filter(line => line.includes('::'))
      .map(line => {
        const parts = line.trim().split('::');
        return {
          file: parts[0],
          test: parts[1] || parts[0],
          fullPath: line.trim()
        };
      });

    res.json({ tests });
  } catch (err) {
    console.error('Error listing tests:', err);
    res.status(500).json({ error: 'Failed to list tests', details: err.message });
  }
});

// Run specific test(s)
app.post('/api/tests/run', async (req, res) => {
  try {
    const { testPath, testType = 'automated' } = req.body;
    const testRunId = new Date().toISOString().replace(/[:.]/g, '-');
    const runDir = path.join(TEST_RESULTS_DIR, testType, testRunId);

    await fs.mkdir(runDir, { recursive: true });

    const metadata = {
      test_run_id: testRunId,
      test_type: testType,
      test_name: testPath || 'all',
      timestamp: new Date().toISOString(),
      status: 'running',
      test_file: testPath
    };

    await fs.writeFile(
      path.join(runDir, 'metadata.json'),
      JSON.stringify(metadata, null, 2)
    );

    // Update index
    const indexPath = path.join(TEST_RESULTS_DIR, 'index.json');
    let index = { test_runs: [] };
    try {
      const indexData = await fs.readFile(indexPath, 'utf-8');
      index = JSON.parse(indexData);
    } catch (err) {
      // Index doesn't exist yet
    }

    index.test_runs.unshift({
      testRunId: testRunId,
      testPath: testPath,
      testType: testType,
      timestamp: metadata.timestamp,
      status: 'running'
    });
    index.last_updated = new Date().toISOString();

    await fs.writeFile(indexPath, JSON.stringify(index, null, 2));

    // Start test execution
    const testCommand = testPath
      ? `source venv/bin/activate && python -m pytest ${testPath} -v --tb=short`
      : `source venv/bin/activate && python -m pytest tests/ -v --tb=short`;

    const testProcess = spawn(testCommand, {
      cwd: __dirname,
      shell: '/bin/bash'
    });

    let output = '';
    testProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    testProcess.stderr.on('data', (data) => {
      output += data.toString();
    });

    testProcess.on('close', async (code) => {
      metadata.status = code === 0 ? 'passed' : 'failed';
      metadata.exit_code = code;

      await fs.writeFile(
        path.join(runDir, 'pytest-output.txt'),
        output
      );

      await fs.writeFile(
        path.join(runDir, 'metadata.json'),
        JSON.stringify(metadata, null, 2)
      );

      // Update index
      const updatedIndex = JSON.parse(await fs.readFile(indexPath, 'utf-8'));
      const runIndex = updatedIndex.test_runs.findIndex(r => r.testRunId === testRunId);
      if (runIndex !== -1) {
        updatedIndex.test_runs[runIndex].status = metadata.status;
        updatedIndex.test_runs[runIndex].testPath = testPath;
      }
      updatedIndex.last_updated = new Date().toISOString();
      await fs.writeFile(indexPath, JSON.stringify(updatedIndex, null, 2));

      testRunsInProgress.delete(testRunId);
    });

    testRunsInProgress.set(testRunId, { process: testProcess, output: () => output });

    res.json({ success: true, testRunId, status: 'started' });
  } catch (err) {
    console.error('Error running tests:', err);
    res.status(500).json({ error: 'Failed to run tests' });
  }
});

// Get test run results
app.get('/api/tests/results/:testRunId', async (req, res) => {
  try {
    const { testRunId } = req.params;

    // Find test run directory
    const automatedDir = path.join(TEST_RESULTS_DIR, 'automated', testRunId);
    const manualDir = path.join(TEST_RESULTS_DIR, 'manual', testRunId);

    let runDir;
    if (await fs.access(automatedDir).then(() => true).catch(() => false)) {
      runDir = automatedDir;
    } else if (await fs.access(manualDir).then(() => true).catch(() => false)) {
      runDir = manualDir;
    } else {
      return res.status(404).json({ error: 'Test run not found' });
    }

    const metadata = JSON.parse(await fs.readFile(path.join(runDir, 'metadata.json'), 'utf-8'));

    let output = '';
    try {
      output = await fs.readFile(path.join(runDir, 'pytest-output.txt'), 'utf-8');
    } catch (err) {
      // Output not yet available
      if (testRunsInProgress.has(testRunId)) {
        output = testRunsInProgress.get(testRunId).output();
      }
    }

    res.json({ metadata, output, status: metadata.status });
  } catch (err) {
    console.error('Error getting test results:', err);
    res.status(500).json({ error: 'Failed to get test results' });
  }
});

// Get test history
app.get('/api/tests/history', async (req, res) => {
  try {
    const indexPath = path.join(TEST_RESULTS_DIR, 'index.json');
    const index = JSON.parse(await fs.readFile(indexPath, 'utf-8'));
    res.json(index);
  } catch (err) {
    console.error('Error getting test history:', err);
    res.json({ test_runs: [], last_updated: new Date().toISOString() });
  }
});

// Get use case details
app.get('/api/tests/use-case/:ucNumber', async (req, res) => {
  try {
    const { ucNumber } = req.params;
    const ucKey = `UC-${ucNumber.padStart(3, '0')}`;

    const useCasesPath = path.join(__dirname, 'data', 'use-case-descriptions.json');
    const useCases = JSON.parse(await fs.readFile(useCasesPath, 'utf-8'));

    if (!useCases[ucKey]) {
      return res.status(404).json({ error: 'Use case not found' });
    }

    res.json(useCases[ucKey]);
  } catch (err) {
    console.error('Error getting use case details:', err);
    res.status(500).json({ error: 'Failed to load use case details' });
  }
});

// === DATA EXPLORER ENDPOINTS ===

app.get('/api/data-explorer/:testRunId', async (req, res) => {
  try {
    const { testRunId } = req.params;

    const automatedDir = path.join(TEST_RESULTS_DIR, 'automated', testRunId);
    const manualDir = path.join(TEST_RESULTS_DIR, 'manual', testRunId);

    let runDir;
    if (await fs.access(automatedDir).then(() => true).catch(() => false)) {
      runDir = automatedDir;
    } else if (await fs.access(manualDir).then(() => true).catch(() => false)) {
      runDir = manualDir;
    } else {
      return res.status(404).json({ error: 'Test run not found' });
    }

    const metadata = JSON.parse(await fs.readFile(path.join(runDir, 'metadata.json'), 'utf-8'));

    let sourceData = null;
    let changes = null;

    try {
      sourceData = JSON.parse(await fs.readFile(path.join(runDir, 'source-data.json'), 'utf-8'));
    } catch (err) {
      // Source data not available
    }

    try {
      changes = JSON.parse(await fs.readFile(path.join(runDir, 'data-changes.json'), 'utf-8'));
    } catch (err) {
      // Changes not available
    }

    res.json({ metadata, sourceData, changes });
  } catch (err) {
    console.error('Error in data explorer:', err);
    res.status(500).json({ error: 'Failed to load data explorer data' });
  }
});

// === MANUAL IMPORT ENDPOINTS ===

const multer = require('multer');
const upload = multer({ dest: path.join(TEST_RESULTS_DIR, 'uploads/') });

app.post('/api/import/upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const fileId = uuidv4();
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const uploadDir = path.join(TEST_RESULTS_DIR, 'manual', `${timestamp}_${fileId}`);

    await fs.mkdir(uploadDir, { recursive: true });

    const ext = path.extname(req.file.originalname);
    const newPath = path.join(uploadDir, `source${ext}`);
    await fs.rename(req.file.path, newPath);

    const metadata = {
      file_id: fileId,
      test_run_id: `${timestamp}_${fileId}`,
      test_type: 'manual',
      original_filename: req.file.originalname,
      timestamp: new Date().toISOString(),
      status: 'uploaded',
      file_size: req.file.size
    };

    await fs.writeFile(
      path.join(uploadDir, 'metadata.json'),
      JSON.stringify(metadata, null, 2)
    );

    res.json({ success: true, fileId, testRunId: metadata.test_run_id });
  } catch (err) {
    console.error('Error uploading file:', err);
    res.status(500).json({ error: 'Failed to upload file' });
  }
});

// === REPORTS ENDPOINTS ===

app.get('/api/reports/summary', async (req, res) => {
  try {
    const indexPath = path.join(TEST_RESULTS_DIR, 'index.json');
    const index = JSON.parse(await fs.readFile(indexPath, 'utf-8'));

    const summary = {
      total_runs: index.test_runs.length,
      passed: index.test_runs.filter(r => r.status === 'passed').length,
      failed: index.test_runs.filter(r => r.status === 'failed').length,
      running: index.test_runs.filter(r => r.status === 'running').length,
      last_run: index.test_runs[0] || null
    };

    res.json(summary);
  } catch (err) {
    console.error('Error getting summary:', err);
    res.json({ total_runs: 0, passed: 0, failed: 0, running: 0, last_run: null });
  }
});

app.listen(PORT, () => {
  console.log(`SIS Testing Web App running on http://localhost:${PORT}`);
  console.log(`Open http://localhost:${PORT}/app.html to view the application`);
  if (!process.env.ANTHROPIC_API_KEY) {
    console.warn('\n⚠️  ANTHROPIC_API_KEY not set. AI features will not work.');
    console.warn('Set it with: export ANTHROPIC_API_KEY=your_key_here\n');
  }
});
